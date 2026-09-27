import re
from .config import settings
from .retriever import HybridRetriever
from .reranker import Reranker
from .llm import LLMWrapper
from .tools import router
from .tracer import get_tracer
from .citation_validator import validate_answer
from ingestion.loader import load_documents
from ingestion.chunker import chunk_all

class AgentOrchestrator:
    def __init__(self):
        self.tracer=get_tracer()
        docs=load_documents(settings.data_path)
        chunks=chunk_all(docs,settings.chunk_size,settings.chunk_overlap)
        # Reuse a compatible on-disk index; rebuild only when source chunks change.
        self.retriever=HybridRetriever(chunks,settings.embedding_model,index_dir=settings.index_path,force_rebuild=settings.force_rebuild_index)
        self.reranker=Reranker(settings.reranker_model,settings.reranker_enabled)
        self.llm=LLMWrapper(); self._doc_count=len(docs); self._ready=True

    def is_ready(self): return self._ready and self._doc_count>0
    def doc_count(self): return self._doc_count

    def _calculator_expression(self,q):
        if not re.search(r"\d",q) or not re.search(r"(?:[+*/%]|\d\s+-\s+\d|calculate|compute|what is)",q.lower()): return None
        candidates=re.findall(r"[0-9.()+*/%\s-]{3,}",q)
        return max((x.strip() for x in candidates if re.search(r"\d",x) and re.search(r"[+*/%-]",x)),key=len,default=None)

    @staticmethod
    def _grounded_fallback(reranked):
        if not reranked: return "I don't have enough information in the knowledge base to answer that."
        parts=[]
        for c in reranked[:3]:
            text=re.sub(r"\s+"," ",c["text"]).strip()
            sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]
            if sentences:
                parts.append(f"{sentences[0]} [{c['doc_id']}:{c['chunk_id']}]")
        return " ".join(parts) or "I don't have enough information in the knowledge base to answer that."

    async def run(self,question,trace_id,top_k=None,require_citations=True):
        top_k=top_k or settings.top_k; spans=[]
        s=self.tracer.start_span("retrieval",trace_id); retrieved=self.retriever.retrieve(question,settings.retrieval_candidates,settings.hybrid_alpha); s.finish(candidate_count=len(retrieved),scores=[r["score"] for r in retrieved]); spans.append(s.to_dict())
        s=self.tracer.start_span("rerank",trace_id); reranked=self.reranker.rerank(question,retrieved,top_k); s.finish(candidate_count=len(retrieved),result_count=len(reranked)); spans.append(s.to_dict())
        tool_calls=[]; history=""; expr=self._calculator_expression(question)
        if expr:
            s=self.tracer.start_span("tool_call",trace_id); result=router.execute("calculator",{"expression":expr}); tool_calls.append(result); history=f"calculator({expr})={result.get('result') if 'result' in result else result.get('error')}"; s.finish(tool="calculator",args={"expression":expr},result=result); spans.append(s.to_dict())
        context="\n".join(f"[{c['doc_id']}:{c['chunk_id']}] {c['text']}" for c in reranked)
        s=self.tracer.start_span("llm_generation",trace_id); llm=self.llm.generate(context,question,history); s.finish(model=settings.openai_model if settings.llm_provider=="openai" else "mock",usage=llm["usage"],cost=llm["cost"]); spans.append(s.to_dict())
        citations=[{"doc_id":c["doc_id"],"chunk_id":c["chunk_id"],"text":c["text"][:500],"score":c.get("rerank_score",c.get("score",0))} for c in reranked]

        validation=validate_answer(llm["answer"],citations) if require_citations else {"valid":True,"score":1.0,"claims":[]}
        # Never manufacture a citation. If generation is not verifiably grounded,
        # return an extractive answer whose citations are known to be valid.
        if require_citations and not validation["valid"]:
            llm["answer"] = self._grounded_fallback(reranked)
            validation=validate_answer(llm["answer"],citations)
        self.tracer.log_trace(trace_id,spans)
        return {"answer":llm["answer"],"citations":citations,"citation_validation":validation,"trace":spans,"usage":llm["usage"],"cost":llm["cost"],"retrieval_scores":[c.get("rerank_score",c.get("score",0)) for c in reranked],"tool_calls":tool_calls}
