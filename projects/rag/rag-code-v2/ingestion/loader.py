import json
from pathlib import Path
from typing import List, Dict

def load_documents(path="data/docs.json")->List[Dict]:
    p=Path(path)
    if not p.exists():
        demo=[{"id":f"doc_{i}","title":f"Sample Doc {i}","text":f"Document {i}: RAG stands for Retrieval Augmented Generation. Retrieval finds relevant knowledge and generation produces a grounded answer. Agent routing can use validated tools. Evaluation measures retrieval and answer quality."} for i in range(1,11)]
        p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(demo,indent=2),encoding="utf-8")
    data=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data,list): raise ValueError("Document corpus must be a JSON list")
    for d in data:
        if not all(k in d for k in ("id","text")): raise ValueError("Each document requires id and text")
    return data
