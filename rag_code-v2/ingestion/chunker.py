from typing import List,Dict

def chunk_document(doc:Dict,chunk_size=300,overlap=50)->List[Dict]:
    if overlap>=chunk_size: raise ValueError("overlap must be smaller than chunk_size")
    words=doc["text"].split(); out=[]; step=chunk_size-overlap
    for n,i in enumerate(range(0,len(words),step)):
        text=" ".join(words[i:i+chunk_size]).strip()
        if not text: continue
        out.append({"doc_id":str(doc["id"]),"chunk_id":f"{doc['id']}_c{n}","text":text,"title":doc.get("title","")})
    return out

def chunk_all(docs,chunk_size=300,overlap=50):
    return [c for d in docs for c in chunk_document(d,chunk_size,overlap)]
