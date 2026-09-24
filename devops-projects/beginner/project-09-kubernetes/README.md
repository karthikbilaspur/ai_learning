# Project 9 — Container Orchestration with Kubernetes

Runs the same container image from Project 4 under Kubernetes instead of
plain Docker Compose — with multiple replicas and automatic health checks.

## What's here
- `k8s/namespace.yaml` — a `devops-starter` namespace so this stack doesn't
  mix with anything else in the cluster
- `k8s/configmap.yaml` — sets `APP_ENV`, same as `docker-compose.yml` does
- `k8s/deployment.yaml` — 2 replicas, readiness/liveness probes on `/health`
- `k8s/service.yaml` — exposes the app inside the cluster (`NodePort`)
- Everything from Project 8

## What to do

1. Read `k8s/README.md` first.
2. Start Minikube and build the image *inside* it:
   ```bash
   minikube start
   eval $(minikube docker-env)
   docker build -t devops-starter:local .
   ```
3. Apply every manifest and check the namespace:
   ```bash
   kubectl apply -f k8s/
   kubectl get pods -n devops-starter
   minikube service devops-app -n devops-starter
   ```
4. Try scaling it up:
   ```bash
   kubectl scale deployment devops-app -n devops-starter --replicas=3
   kubectl get pods -n devops-starter
   ```
5. Clean up:
   ```bash
   kubectl delete -f k8s/
   ```

## Concepts to know before moving on
- Pod vs. Deployment vs. Service — what each one is responsible for
- What a readiness probe protects against (traffic hitting a pod before
  it's ready) vs. a liveness probe (restarting a pod that's stuck)
- Why a ConfigMap exists instead of hardcoding env vars into the Deployment

Next: **Project 10 — Monitoring with Prometheus & Grafana**
