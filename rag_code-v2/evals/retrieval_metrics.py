from typing import List,Dict
def _match(r,expected): return r.get("doc_id")==expected or str(expected) in str(r.get("doc_id"))
def recall_at_k(retrieved:List[Dict],expected_doc:str,k=5): return 1.0 if any(_match(r,expected_doc) for r in retrieved[:k]) else 0.0
def mrr(retrieved:List[Dict],expected_doc:str):
 for i,r in enumerate(retrieved,1):
  if _match(r,expected_doc): return 1/i
 return 0.0
def evaluate_retrieval(results):
 n=max(1,len(results)); return {"Recall@5":sum(r["recall@5"] for r in results)/n,"MRR":sum(r["mrr"] for r in results)/n,"count":len(results)}
