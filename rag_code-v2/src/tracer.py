import time, threading, uuid
from typing import Any

class Span:
    def __init__(self,name,trace_id): self.name=name; self.trace_id=trace_id; self.start=time.perf_counter(); self.data={}; self.finished=False
    def finish(self, **data): self.data.update(data); self.data["latency_ms"]=round((time.perf_counter()-self.start)*1000,2); self.finished=True
    def to_dict(self): return {"span":self.name,"trace_id":self.trace_id,**self.data}

class Tracer:
    def __init__(self,max_traces=1000): self.max_traces=max_traces; self.metrics=[]; self.errors=[]; self._lock=threading.Lock()
    def start_span(self,name,trace_id): return Span(name,trace_id)
    def log_trace(self,trace_id,spans):
        with self._lock: self.metrics.append({"trace_id":trace_id,"spans":spans}); self.metrics=self.metrics[-self.max_traces:]
    def log_error(self,trace_id,error):
        with self._lock: self.errors.append({"trace_id":trace_id,"error":error}); self.errors=self.errors[-self.max_traces:]
    def get_dashboard_metrics(self):
        with self._lock: traces=list(self.metrics); errors=list(self.errors)
        lat=[s.get("latency_ms",0) for t in traces for s in t.get("spans",[])]
        return {"trace_count":len(traces),"error_count":len(errors),"recent_traces":traces[-20:],"p95_span_latency_ms":sorted(lat)[max(0,int(len(lat)*.95)-1)] if lat else 0}
_tracer=Tracer()
def get_tracer(): return _tracer
