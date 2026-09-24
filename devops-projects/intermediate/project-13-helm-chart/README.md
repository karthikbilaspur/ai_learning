# Project 13 — Packaging the App as a Helm Chart

Project 9 (beginner series) had four separate, static YAML files. Helm
turns that into one parameterized, versioned, installable package — the
same chart deploys dev, staging, or prod just by swapping a values file.

## What's here
- `devops-starter-chart/Chart.yaml` — chart metadata
- `devops-starter-chart/values.yaml` — defaults
- `devops-starter-chart/values-dev.yaml` / `values-prod.yaml` — environment
  overrides (prod adds resource limits and 3 replicas instead of 1)
- `devops-starter-chart/templates/` — the same Deployment/Service/ConfigMap
  from Project 9, now templated with `{{ .Values.* }}`

## Assumes
A Kubernetes cluster (Minikube is fine) with `helm` installed, and the
`devops-starter:local` image already built (`docker build -t
devops-starter:local .` from the beginner series).

## What to do

1. Lint the chart before installing anything:
   ```bash
   cd devops-starter-chart
   helm lint .
   ```
2. See exactly what Kubernetes YAML the chart would generate, without
   applying it:
   ```bash
   helm template . -f values-dev.yaml
   ```
3. Install it for "dev":
   ```bash
   helm install devops-dev . -f values-dev.yaml
   kubectl get pods
   ```
4. Change something (e.g. `replicaCount` in `values-dev.yaml`) and upgrade
   in place instead of deleting and recreating:
   ```bash
   helm upgrade devops-dev . -f values-dev.yaml
   ```
5. Look at release history and roll back:
   ```bash
   helm history devops-dev
   helm rollback devops-dev 1
   ```
6. Install the *same chart* again as "prod", side by side, using the prod
   values file:
   ```bash
   helm install devops-prod . -f values-prod.yaml
   ```
7. Clean up:
   ```bash
   helm uninstall devops-dev devops-prod
   ```

## Concepts to know before moving on
- Chart vs. Release: one chart, many releases (dev, prod) at once
- `helm template` vs `helm install` — always preview before applying
- Why `helm upgrade`/`rollback` beats manually editing and reapplying YAML
- Values files as the Helm equivalent of Project 12's Terraform `.tfvars`

## Optional: publish it
Package and push the chart to an OCI-compatible registry (GitHub Container
Registry works) so others can `helm install` it without cloning this repo:
```bash
helm package .
helm push devops-starter-0.1.0.tgz oci://ghcr.io/your-username/charts
```

Next: **Project 14 — Ingress, TLS, and Autoscaling**
