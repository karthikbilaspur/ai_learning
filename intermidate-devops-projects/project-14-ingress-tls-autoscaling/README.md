# Project 14 — Ingress, Automated TLS, and Autoscaling

Project 9's Service was a `NodePort` — fine for Minikube, useless for real
traffic. This project adds a proper Ingress with automatic HTTPS
certificates, plus a HorizontalPodAutoscaler so the app scales itself under
load instead of sitting at a fixed 2 replicas.

## What's here
- `k8s/ingress.yaml` — routes `devops-starter.example.com` to the app,
  requests a TLS cert automatically via a `cert-manager.io` annotation
- `k8s/cluster-issuer.yaml` — tells cert-manager to get certs from Let's
  Encrypt
- `k8s/hpa.yaml` — scales the Deployment between 2 and 6 replicas based on
  CPU usage
- `k8s/deployment.yaml` — same app, now with `resources.requests/limits`
  set (the HPA needs these to calculate utilization)

## Assumes
A real Kubernetes cluster reachable from the internet (a cloud cluster,
not Minikube) with an nginx-ingress controller installed, a domain you
control, and the `metrics-server` add-on for the HPA to read CPU stats.

## What to do

1. Install an ingress controller and cert-manager (once per cluster):
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.0/deploy/static/provider/cloud/deploy.yaml
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
   ```
2. Edit `k8s/ingress.yaml` and `k8s/cluster-issuer.yaml` — replace
   `devops-starter.example.com` and the email with your own.
3. Point your domain's DNS `A` record at the ingress controller's external
   IP (`kubectl get svc -n ingress-nginx`).
4. Apply everything:
   ```bash
   kubectl apply -f k8s/
   ```
5. Watch cert-manager issue the certificate:
   ```bash
   kubectl get certificate -n devops-starter
   ```
6. Load-test the app to watch the HPA react (needs `hey` or similar):
   ```bash
   kubectl get hpa -n devops-starter -w
   hey -z 60s -c 50 https://devops-starter.example.com/
   ```

## Concepts to know before moving on
- Why Ingress replaces NodePort for real traffic — one entry point, host
  and path-based routing
- What `resources.requests` are used for by the HPA (vs. `limits`, which
  caps usage)
- The ACME HTTP-01 challenge cert-manager uses to prove domain ownership

Next: **Project 15 — Blue-Green / Canary Deployments**
