from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="DevOps Starter API", version="1.0.0")

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {
        "message": "DevOps starter app is running",
        "environment": "development"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/info")
def info():
    return {
        "project": "Complete DevOps Starter",
        "stack": ["Docker", "Nginx", "GitHub Actions", "Terraform", "Kubernetes", "Prometheus", "Grafana"]
    }
