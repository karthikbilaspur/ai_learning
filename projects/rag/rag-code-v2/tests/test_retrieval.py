from ingestion.loader import load_documents
from ingestion.chunker import chunk_all
from src.retriever import HybridRetriever
def test_retrieval():
 r=HybridRetriever(chunk_all(load_documents())); out=r.retrieve("What is RAG?",3); assert len(out)==3 and "score" in out[0]

def test_index_persistence(tmp_path):
    chunks=chunk_all(load_documents(),)
    first=HybridRetriever(chunks,index_dir=tmp_path)
    second=HybridRetriever(chunks,index_dir=tmp_path)
    assert second._load() is True
    assert second.retrieve("What is RAG?",3)[0]["doc_id"] == first.retrieve("What is RAG?",3)[0]["doc_id"]
