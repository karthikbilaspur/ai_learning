from pathlib import Path
from typing import List
import hashlib, json, pickle
import numpy as np
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    class BM25Okapi:
        def __init__(self, corpus):
            self.corpus=corpus; self.df={}; self.avgdl=sum(map(len,corpus))/max(1,len(corpus))
            for row in corpus:
                for t in set(row): self.df[t]=self.df.get(t,0)+1
        def get_scores(self, query):
            import math
            n=len(self.corpus); out=[]; k1=1.5; b=.75
            for row in self.corpus:
                dl=len(row); score=0.0
                for term in query:
                    f=row.count(term)
                    if not f: continue
                    idf=math.log(1+(n-self.df.get(term,0)+.5)/(self.df.get(term,0)+.5))
                    score += idf*(f*(k1+1))/(f+k1*(1-b+b*dl/max(1,self.avgdl)))
                out.append(score)
            return np.asarray(out)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    SentenceTransformer=None; faiss=None
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

class HybridRetriever:
    """Persistent hybrid BM25 + dense/TF-IDF retriever."""
    VERSION = 2

    def __init__(self, chunks=None, embedding_model="sentence-transformers/all-MiniLM-L6-v2", index_dir=None, force_rebuild=False):
        self.index_dir = Path(index_dir) if index_dir else None
        self.embedding_model_name = embedding_model
        self.model = None; self.index = None; self.backend = None
        if self.index_dir and not force_rebuild and self._load():
            return
        if not chunks:
            raise ValueError("Cannot build retriever with no chunks")
        self._build(chunks)
        if self.index_dir:
            self.save()

    def _fingerprint(self, chunks):
        payload = [{k:c.get(k) for k in ("doc_id","chunk_id","text")} for c in chunks]
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def _build(self, chunks):
        self.chunks=chunks; self.texts=[c["text"] for c in chunks]
        self.bm25=BM25Okapi([t.lower().split() for t in self.texts])
        self.backend="tfidf"
        if SentenceTransformer and faiss:
            self.model=SentenceTransformer(self.embedding_model_name)
            emb=self.model.encode(self.texts,normalize_embeddings=True,show_progress_bar=False)
            self.embeddings=np.asarray(emb,dtype="float32")
            self.index=faiss.IndexFlatIP(self.embeddings.shape[1]); self.index.add(self.embeddings)
            self.backend="dense+bm25"
        else:
            self.vectorizer=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True); self.tfidf_matrix=self.vectorizer.fit_transform(self.texts)

    def save(self):
        if not self.index_dir: return
        self.index_dir.mkdir(parents=True, exist_ok=True)
        (self.index_dir / "chunks.json").write_text(json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        meta={"version":self.VERSION,"fingerprint":self._fingerprint(self.chunks),"embedding_model":self.embedding_model_name,"backend":self.backend,"count":len(self.chunks)}
        (self.index_dir / "manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        if self.backend == "dense+bm25":
            np.save(self.index_dir / "embeddings.npy", self.embeddings)
            faiss.write_index(self.index, str(self.index_dir / "faiss.index"))
        else:
            with open(self.index_dir / "tfidf.pkl", "wb") as f: pickle.dump((self.vectorizer, self.tfidf_matrix), f)

    def _load(self):
        manifest_path=self.index_dir / "manifest.json"
        chunks_path=self.index_dir / "chunks.json"
        if not manifest_path.exists() or not chunks_path.exists(): return False
        try:
            meta=json.loads(manifest_path.read_text()); chunks=json.loads(chunks_path.read_text())
            if meta.get("version") != self.VERSION or meta.get("embedding_model") != self.embedding_model_name: return False
            if meta.get("fingerprint") != self._fingerprint(chunks): return False
            self.chunks=chunks; self.texts=[c["text"] for c in chunks]
            self.bm25=BM25Okapi([t.lower().split() for t in self.texts])
            self.backend=meta["backend"]
            if self.backend == "dense+bm25" and SentenceTransformer and faiss and (self.index_dir/"faiss.index").exists():
                self.model=SentenceTransformer(self.embedding_model_name); self.index=faiss.read_index(str(self.index_dir/"faiss.index")); self.embeddings=np.load(self.index_dir/"embeddings.npy")
            elif self.backend == "tfidf" and (self.index_dir/"tfidf.pkl").exists():
                with open(self.index_dir/"tfidf.pkl", "rb") as f: self.vectorizer,self.tfidf_matrix=pickle.load(f)
            else: return False
            return True
        except Exception:
            return False

    def retrieve(self,query,top_k=5,alpha=.6):
        k=min(max(1,top_k),len(self.chunks)); bm=np.asarray(self.bm25.get_scores(query.lower().split()),dtype=float); bm=(bm-bm.min())/(bm.max()-bm.min()+1e-9)
        if self.model:
            q=self.model.encode([query],normalize_embeddings=True); scores,indices=self.index.search(np.asarray(q,dtype="float32"),len(self.chunks)); dense_map=np.zeros(len(self.chunks))
            for score,idx in zip(scores[0],indices[0]): dense_map[idx]=score
        else: dense_map=cosine_similarity(self.vectorizer.transform([query]),self.tfidf_matrix)[0]
        hybrid=alpha*dense_map+(1-alpha)*bm; inds=np.argsort(-hybrid)[:k]
        return [{**self.chunks[i],"score":float(hybrid[i]),"bm25":float(bm[i]),"dense":float(dense_map[i])} for i in inds]
