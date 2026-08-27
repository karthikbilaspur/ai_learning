
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app
import time
from .logging_conf import setup_logging
from .config import settings
from .database import Base, engine
from .api.routes import router
from .exceptions import AppException, app_exception_handler, generic_exception_handler
import structlog

setup_logging(settings.LOG_LEVEL)
logger = structlog.get_logger()

# Create tables if not using alembic in dev
Base.metadata.create_all(bind=engine)

app = FastAPI(title="task_python - Unified Tool Agent", version="3.0.0", description="Productionized agent from 9 standalone scripts")

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method","endpoint","status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Latency", ["endpoint"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(time.time()-start)
    return response

app.include_router(router, prefix="/api")

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health", tags=["monitoring"])
def health():
    return {"status": "ok", "version": "3.0.0", "env": settings.LOG_LEVEL, "tools": 9}

@app.get("/", tags=["root"])
def root():
    return {"message": "task_python agent running. Docs at /docs", "health": "/health", "metrics": "/metrics"}

logger.info("app_started", version="3.0.0")
