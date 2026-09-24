"""CPU-friendly compression benchmark: FP32 vs dynamic INT8 vs magnitude sparsity."""
import argparse,time,os,psutil,torch
from transformers import AutoModelForSequenceClassification,AutoTokenizer
from prune import magnitude_prune,check_sparsity

def bench(model,tok,text='This is a benchmark.',runs=20):
    model.eval();dev=next(model.parameters()).device;inputs=tok(text,return_tensors='pt').to(dev)
    with torch.no_grad():
        for _ in range(3): model(**inputs)
    t=time.perf_counter()
    with torch.no_grad():
        for _ in range(runs): model(**inputs)
    return (time.perf_counter()-t)/runs*1000

def main(model_id='distilbert-base-uncased'):
    tok=AutoTokenizer.from_pretrained(model_id); base=AutoModelForSequenceClassification.from_pretrained(model_id)
    results=[{'variant':'fp32','latency_ms':bench(base,tok),'params':sum(p.numel() for p in base.parameters()),'sparsity':check_sparsity(base)}]
    q=torch.quantization.quantize_dynamic(base,{torch.nn.Linear},dtype=torch.qint8)
    results.append({'variant':'dynamic_int8','latency_ms':bench(q,tok),'params':sum(p.numel() for p in q.parameters()),'sparsity':check_sparsity(q)})
    pr=magnitude_prune(AutoModelForSequenceClassification.from_pretrained(model_id),.5)
    results.append({'variant':'pruned_50pct','latency_ms':bench(pr,tok),'params':sum(p.numel() for p in pr.parameters()),'sparsity':check_sparsity(pr)})
    for r in results: print(r)
if __name__=='__main__': main()
