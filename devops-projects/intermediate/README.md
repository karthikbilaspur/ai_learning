# Intermediate DevOps Starter — Projects 11–20

The follow-up to the beginner series (Projects 1–10). Each project here
assumes you're comfortable with Docker, Compose, basic CI, basic Terraform,
and basic Kubernetes, and adds exactly one new piece of real-world
infrastructure on top of that foundation.

| # | Project | Adds |
|---|---------|------|
| 11 | [project-11-gitops-argocd](project-11-gitops-argocd/) | GitOps deployment with ArgoCD |
| 12 | [project-12-terraform-multi-env](project-12-terraform-multi-env/) | Terraform modules + remote state across dev/staging/prod |
| 13 | [project-13-helm-chart](project-13-helm-chart/) | Packaging the app as a Helm chart |
| 14 | [project-14-ingress-tls-autoscaling](project-14-ingress-tls-autoscaling/) | Ingress, automated TLS, and autoscaling |
| 15 | [project-15-blue-green-canary](project-15-blue-green-canary/) | Blue-green / canary deployments |
| 16 | [project-16-centralized-logging](project-16-centralized-logging/) | Centralized logging with Loki + Grafana |
| 17 | [project-17-secrets-management](project-17-secrets-management/) | Secrets management with Vault |
| 18 | [project-18-service-mesh](project-18-service-mesh/) | Service mesh basics with Istio |
| 19 | [project-19-distributed-tracing](project-19-distributed-tracing/) | Distributed tracing with OpenTelemetry + Jaeger |
| 20 | [project-20-database-backup-restore](project-20-database-backup-restore/) | A stateful database with automated backup/restore |

## How to use this

Same idea as the beginner series: each folder is self-contained with its
own README, working config files, and a list of concepts to know before
moving on. Go in order, or jump to whichever topic you need. These projects
build on the app and cluster from **Project 10** of the beginner series —
each README says exactly what it assumes you already have running.

## Shared docs
- [docs/prerequisites.md](docs/prerequisites.md) — tools you'll need installed across these 10 projects
