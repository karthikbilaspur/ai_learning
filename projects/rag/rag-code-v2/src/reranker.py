try:
 from sentence_transformers import CrossEncoder
except ImportError: CrossEncoder=None
class Reranker:
 def __init__(self,model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",enabled=True):
  self.model=CrossEncoder(model_name) if enabled and CrossEncoder else None
 def rerank(self,query,docs,top_k=5):
  if not docs:return []
  docs=[dict(d) for d in docs]
  if self.model:
   for d,s in zip(docs,self.model.predict([(query,d["text"]) for d in docs])): d["rerank_score"]=float(s)
   docs.sort(key=lambda d:d["rerank_score"],reverse=True)
  else:
   docs.sort(key=lambda d:d.get("score",0),reverse=True)
   for d in docs:d["rerank_score"]=d.get("score",0)
  return docs[:top_k]
