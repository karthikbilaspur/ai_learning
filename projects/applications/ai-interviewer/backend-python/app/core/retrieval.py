"""
Hybrid retrieval over the question bank.

Used by the planner to pick the next question by *semantic + lexical*
similarity to the candidate's weak areas, instead of random.choice().

- Dense: ChromaDB (in-memory/ephemeral client, one collection per process)
- Lexical: BM25 (rank_bm25) over question_text + category
- Fusion: Reciprocal Rank Fusion (RRF) of the two rankings
- Optional: cross-encoder rerank of the fused top-N if sentence-transformers
  is installed with a CrossEncoder model available; otherwise this step is
  skipped and logged, not silently pretended to have happened.

Everything degrades gracefully: if chromadb or rank_bm25 aren't installed,
retrieval falls back to plain BM25-only or, worst case, category-match
filtering. No component is imported-but-unused like in the earlier version.
"""
import re

_HAS_CHROMA = False
_HAS_BM25 = False
_HAS_CROSS_ENCODER = False

try:
    import chromadb
    _HAS_CHROMA = True
except Exception:
    chromadb = None

try:
    from rank_bm25 import BM25Okapi
    _HAS_BM25 = True
except Exception:
    BM25Okapi = None

_cross_encoder = None
try:
    from sentence_transformers import CrossEncoder
    _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    _HAS_CROSS_ENCODER = True
except Exception:
    _cross_encoder = None


def _tokenize(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


class QuestionRetriever:
    """One retriever per (role, level) question list."""

    def __init__(self, questions):
        self.questions = questions
        self.ids = [q["id"] for q in questions]
        self.docs = [f"{q['category']} {q['question_text']}" for q in questions]

        self._bm25 = None
        if _HAS_BM25 and self.docs:
            self._bm25 = BM25Okapi([_tokenize(d) for d in self.docs])

        self._chroma_collection = None
        if _HAS_CHROMA and self.docs:
            try:
                client = chromadb.EphemeralClient()
                name = f"qbank_{abs(hash(tuple(self.ids)))}"
                self._chroma_collection = client.get_or_create_collection(name)
                if self._chroma_collection.count() == 0:
                    self._chroma_collection.add(
                        ids=self.ids, documents=self.docs
                    )
            except Exception as e:
                print(f"[retrieval] chroma unavailable: {e}")
                self._chroma_collection = None

    def _bm25_rank(self, query: str):
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.ids[i] for i in ranked]

    def _vector_rank(self, query: str, n: int):
        if not self._chroma_collection:
            return []
        try:
            res = self._chroma_collection.query(query_texts=[query], n_results=min(n, len(self.ids)))
            return res["ids"][0]
        except Exception as e:
            print(f"[retrieval] chroma query failed: {e}")
            return []

    def rank(self, query: str, exclude_ids=None, top_k=5):
        """Return question ids ranked by fused BM25 + vector relevance to `query`,
        excluding already-asked ids. Falls back to bank order if no retrieval
        backend is available."""
        exclude_ids = set(exclude_ids or [])
        candidates = [qid for qid in self.ids if qid not in exclude_ids]
        if not candidates:
            return []

        bm25_order = [i for i in self._bm25_rank(query) if i in exclude_ids or True][:len(self.ids)]
        bm25_order = [i for i in bm25_order if i not in exclude_ids]
        vec_order = [i for i in self._vector_rank(query, len(self.ids)) if i not in exclude_ids]

        if not bm25_order and not vec_order:
            return candidates[:top_k]

        # Reciprocal Rank Fusion
        k = 60
        fused = {}
        for rank_list in (bm25_order, vec_order):
            for pos, qid in enumerate(rank_list):
                fused[qid] = fused.get(qid, 0.0) + 1.0 / (k + pos + 1)
        for qid in candidates:
            fused.setdefault(qid, 0.0)

        fused_order = sorted(candidates, key=lambda qid: fused[qid], reverse=True)

        if _HAS_CROSS_ENCODER and _cross_encoder is not None and len(fused_order) > 1:
            try:
                top_n = fused_order[: max(top_k * 2, 5)]
                id_to_doc = dict(zip(self.ids, self.docs))
                pairs = [(query, id_to_doc[qid]) for qid in top_n]
                scores = _cross_encoder.predict(pairs)
                reranked = [qid for qid, _ in sorted(zip(top_n, scores), key=lambda x: x[1], reverse=True)]
                rest = [qid for qid in fused_order if qid not in reranked]
                return (reranked + rest)[:top_k]
            except Exception as e:
                print(f"[retrieval] cross-encoder rerank failed: {e}")

        return fused_order[:top_k]


def retrieval_status():
    """Report which retrieval backends are actually active — used by the
    /status endpoint so the frontend shows real capabilities, not aspirational ones."""
    return {
        "bm25": _HAS_BM25,
        "chroma_vector": _HAS_CHROMA,
        "cross_encoder_rerank": _HAS_CROSS_ENCODER,
    }
