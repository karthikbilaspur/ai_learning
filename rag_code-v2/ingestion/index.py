from .loader import load_documents
from .chunker import chunk_all
from src.retriever import HybridRetriever
from src.config import settings

def build_indexes(force_rebuild=False):
    docs=load_documents(settings.data_path)
    chunks=chunk_all(docs,settings.chunk_size,settings.chunk_overlap)
    r=HybridRetriever(chunks,settings.embedding_model,index_dir=settings.index_path,force_rebuild=force_rebuild)
    print(f"Indexed {len(docs)} docs / {len(chunks)} chunks using {r.backend} at {settings.index_path}")
    return r
if __name__=="__main__": build_indexes()
