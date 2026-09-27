"""
Singleton accessors for the embedding model, cross-encoder reranker, and
per-repo Chroma collections. Kept as module-level singletons because
loading these models is slow and they're stateless w.r.t. which repo is
being queried.
"""

import logging

import chromadb

logger = logging.getLogger("talktorepo.vectorstore")

_chroma_collections: dict[str, "chromadb.Collection"] = {}
_embed_model = None
_cross_model = None


def get_chroma(repo_id: str):
    if repo_id not in _chroma_collections:
        client = chromadb.PersistentClient(path=f"./chroma_db/{repo_id}")
        _chroma_collections[repo_id] = client.get_or_create_collection(name=f"repo_{repo_id}")
    return _chroma_collections[repo_id]


def get_embedding_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer

        # nomic-embed-text is a stronger embedding for code but requires
        # `trust_remote_code=True`, i.e. it runs custom Python shipped in
        # the model repo on HuggingFace. That's a real supply-chain trust
        # decision, not a free lunch — falls back to a safe, no-custom-code
        # model if it's unavailable or you'd rather not opt into that.
        try:
            _embed_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
            logger.info("Loaded nomic-embed-text (trust_remote_code=True).")
        except Exception as exc:
            logger.warning("nomic-embed-text unavailable (%s), falling back to all-MiniLM-L6-v2.", exc)
            _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def get_cross_encoder():
    global _cross_model
    if _cross_model is None:
        from sentence_transformers import CrossEncoder

        _cross_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info("Loaded cross-encoder reranker.")
    return _cross_model
