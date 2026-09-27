import time,uuid,asyncio
from collections import defaultdict,deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.config import settings
class RequestIDMiddleware(BaseHTTPMiddleware):
 async def dispatch(self,request,call_next):
  rid=request.headers.get("X-Request-ID") or str(uuid.uuid4()); request.state.request_id=rid; start=time.perf_counter()
  response=await call_next(request); response.headers["X-Request-ID"]=rid; response.headers["X-Response-Time"]=f"{(time.perf_counter()-start)*1000:.2f}ms"; return response
class RateLimitMiddleware(BaseHTTPMiddleware):
 def __init__(self,app,max_requests=None,window_seconds=None): super().__init__(app); self.max_requests=max_requests or settings.rate_limit_requests; self.window=window_seconds or settings.rate_limit_window_seconds; self.hits=defaultdict(deque); self.lock=asyncio.Lock()
 async def dispatch(self,request,call_next):
  ip=request.client.host if request.client else "unknown"; now=time.monotonic()
  async with self.lock:
   q=self.hits[ip]
   while q and now-q[0]>=self.window:q.popleft()
   if len(q)>=self.max_requests:return JSONResponse(status_code=429,content={"error":"Rate limit exceeded"},headers={"Retry-After":str(self.window)})
   q.append(now)
  return await call_next(request)
