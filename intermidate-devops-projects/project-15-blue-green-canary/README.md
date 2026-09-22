# Project 15 — Blue-Green / Canary Deployments

Every deploy so far has been "replace the old pods with new ones and hope."
This project runs the new version alongside the old one at low traffic
first, so a bad release only affects a fraction of users, and you can pull
it back before it reaches everyone.

## What's here
- `k8s/deployment-stable.yaml` — the current version (`devops-starter:v1`),
  3 replicas
- `k8s/deployment-canary.yaml` — the new version (`devops-starter:v2`), 1
  replica
- `k8s/service.yaml` — selects on `app: devops-app` only (not `track`), so
  it load-balances across *both* deployments — replica ratio becomes the
  traffic split (1:3 here ≈ 25% canary)
- `.github/workflows/canary-deploy.yml` — a manually triggered workflow
  that updates the canary's image and pauses for a health check before
  reminding you to promote it

## Assumes
A Kubernetes cluster with both `v1` and `v2` images of the app already
built and pushed somewhere `kubectl` can pull them from.

## What to do

1. Build and tag two versions of the app (even a trivial change to
   `app/main.py`'s response text is enough to tell them apart):
   ```bash
   docker build -t devops-starter:v1 .
   # make a small change, then:
   docker build -t devops-starter:v2 .
   ```
2. Deploy stable only first:
   ```bash
   kubectl apply -f k8s/namespace.yaml -f k8s/deployment-stable.yaml -f k8s/service.yaml
   ```
3. Curl the service a bunch of times and confirm every response is from v1.
4. Roll out the canary:
   ```bash
   kubectl apply -f k8s/deployment-canary.yaml
   ```
5. Curl again, repeatedly — roughly 1 in 4 responses should now come from
   v2. This is the canary getting real traffic at low volume.
6. **To promote**: update `deployment-stable.yaml`'s image to `v2`, apply
   it, then scale the canary down to 0 (`kubectl scale deployment
   devops-app-canary -n devops-starter --replicas=0`).
   **To roll back**: just delete the canary deployment — stable traffic
   was never touched.

## Concepts to know before moving on
- Canary (gradual, traffic-split) vs. blue-green (instant full cutover
  between two complete environments) — this project builds canary; try
  sketching what blue-green's Service/label setup would look like instead
- Why replica *ratio*, not percentages in code, is doing the traffic
  splitting here — good enough for learning, but a service mesh (Project
  18) gives you precise percentages
- Why the canary needs its own health check before promotion, not just
  "it's running"

Next: **Project 16 — Centralized Logging**
