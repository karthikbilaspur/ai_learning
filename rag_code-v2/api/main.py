import time,uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from .schemas import QueryRequest,QueryResponse,HealthResponse
from .middleware import RequestIDMiddleware,RateLimitMiddleware
from src.agent import AgentOrchestrator
from src.config import settings
from src.tracer import get_tracer
from src.logging import configure_logging
agent=None; tracer=get_tracer()
@asynccontextmanager
async def lifespan(app: FastAPI):
 global agent
 configure_logging(settings.log_level); agent=AgentOrchestrator(); yield; agent=None
app=FastAPI(title=settings.app_name,version=settings.app_version,lifespan=lifespan)
app.add_middleware(RequestIDMiddleware); app.add_middleware(RateLimitMiddleware)
@app.get("/health",response_model=HealthResponse)
async def health(): return {"status":"ok","version":settings.app_version,"eval_gate":"enabled"}
@app.get("/ready")
async def ready(): return {"ready":bool(agent and agent.is_ready()),"docs_indexed":agent.doc_count() if agent else 0}
@app.post("/query",response_model=QueryResponse)
async def query(req:QueryRequest,request:Request):
 if not agent:return JSONResponse(status_code=503,content={"error":"Service not ready"})
 rid=getattr(request.state,"request_id",str(uuid.uuid4())); start=time.perf_counter()
 try:
  r=await agent.run(req.question,rid,req.top_k,True); return {"answer":r["answer"],"citations":r["citations"],"trace_id":rid,"latency_ms":round((time.perf_counter()-start)*1000),"tokens":r["usage"],"cost_usd":r["cost"],"retrieval_scores":r["retrieval_scores"],"tool_calls":r["tool_calls"]}
 except Exception as e:
  tracer.log_error(rid,str(e)); return JSONResponse(status_code=500,content={"error":"Internal query failure","trace_id":rid})
@app.get("/metrics")
async def metrics(): return tracer.get_dashboard_metrics()
