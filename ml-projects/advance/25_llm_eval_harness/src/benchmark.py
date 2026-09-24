"""Reproducible LLM benchmark runner with repeated trials and regression comparison."""
import json, os, statistics, time

def run_repeated(model_fn,prompts,runs=3):
    rows=[]
    for run in range(runs):
        for i,p in enumerate(prompts):
            t=time.perf_counter(); r=model_fn(p); elapsed=time.perf_counter()-t
            rows.append({'run':run,'prompt_id':i,'prompt':p,'response':r,'latency_s':elapsed})
    return rows

def summarize(rows):
    lat=[r['latency_s'] for r in rows]
    return {'n':len(rows),'mean_latency_s':statistics.mean(lat) if lat else 0,'p95_latency_s':sorted(lat)[max(0,int(.95*len(lat))-1)] if lat else 0}

def compare_metrics(before,after):
    out={}
    for k in sorted(set(before)|set(after)):
        if isinstance(before.get(k), (int,float)) and isinstance(after.get(k),(int,float)):
            out[k]={'before':before[k],'after':after[k],'delta':after[k]-before[k]}
    return out
