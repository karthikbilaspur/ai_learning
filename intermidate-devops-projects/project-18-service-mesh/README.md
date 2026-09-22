# Project 18 — Service Mesh Basics with Istio

Project 15's canary split traffic by *replica ratio* — approximate, and
with no automatic retries or mTLS. Istio gives you precise percentage-based
routing, automatic mutual TLS between pods, and retry/circuit-breaking
policies, without touching application code.

## What's here
- `k8s/namespace.yaml` — labeled `istio-injection: enabled` so Istio
  auto-injects its sidecar proxy into every pod
- `k8s/deployment-v1.yaml` / `deployment-v2.yaml` — two versions, both at
  equal replica count this time (traffic splitting is no longer done via
  replica ratio)
- `k8s/destination-rule.yaml` — defines `v1`/`v2` as named "subsets," plus
  outlier detection (auto-eject a pod after 3 consecutive 5xx errors)
- `k8s/virtual-service.yaml` — routes 90% of traffic to v1, 10% to v2, with
  automatic retries on failure

## Assumes
A Kubernetes cluster with `istioctl` installed.

## What to do

1. Install Istio into the cluster:
   ```bash
   istioctl install --set profile=demo -y
   ```
2. Apply everything:
   ```bash
   kubectl apply -f k8s/
   ```
3. Confirm the sidecar got injected (2 containers per pod, not 1):
   ```bash
   kubectl get pods -n devops-starter
   ```
4. Send repeated requests through the mesh and count how many land on v1
   vs v2 — it should trend toward 90/10, precisely, unlike Project 15's
   replica-ratio approximation.
5. Check that traffic between pods is encrypted automatically:
   ```bash
   istioctl proxy-config secrets deploy/devops-app-v1 -n devops-starter
   ```
6. Open Kiali (Istio's dashboard, if installed) to see the live service
   graph and traffic split visually.
7. Change `virtual-service.yaml`'s weights to 50/50, reapply, and watch the
   split shift instantly — no redeploying any pods.

## Concepts to know before moving on
- Sidecar proxy pattern: Istio intercepts traffic without your app code
  knowing the mesh exists
- VirtualService (routing rules) vs. DestinationRule (policies for a
  destination once routed there) — two different jobs
- Why precise weighted routing here beats Project 15's replica-ratio trick,
  and what mTLS between every pod buys you for free

Next: **Project 19 — Distributed Tracing with OpenTelemetry + Jaeger**
