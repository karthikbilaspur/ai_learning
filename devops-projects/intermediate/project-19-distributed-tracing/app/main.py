from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

resource = Resource.create({"service.name": "devops-app"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = FastAPI(title="DevOps Starter API - traced", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
def root():
    return {"message": "DevOps starter app is running", "environment": "development"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/info")
def info():
    # A manual child span, to show tracing something FastAPI's
    # auto-instrumentation doesn't see by itself - e.g. a slow step.
    with tracer.start_as_current_span("build-info-payload"):
        time.sleep(random.uniform(0.05, 0.3))  # simulate variable work
        return {
            "project": "Complete DevOps Starter",
            "stack": ["Docker", "Nginx", "GitHub Actions", "Terraform", "Kubernetes", "Prometheus", "Grafana"],
        }
