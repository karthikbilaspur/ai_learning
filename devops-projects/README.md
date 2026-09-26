# DevOps Complete Portfolio — 30 Projects: Zero to Production

> From Linux & Git to GitOps, Service Mesh & eBPF. 30 standalone, runnable projects that build on each other — the complete DevOps engineering track.

[[DevOps](https://img.shields.io/badge/Track-DevOps-0A66C2?style=for-the-badge)]()
[[Projects](https://img.shields.io/badge/Projects-30-2496ED?style=for-the-badge)]()
[[Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)]()
[[Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes&logoColor=white)]()
[[IaC](https://img.shields.io/badge/IaC-Terraform%20%7C%20Terragrunt-7B42BC)]()

This repo is part of [ai_learning](https://github.com/karthikbilaspur/ai_learning) — focused on shipping production systems, not just tutorials. Every project is self-contained, runnable, and has its own README.

### 🗺️ Learning Roadmap

```
Phase 1: Foundations (1-10)   →   Phase 2: Real-World Infra (11-20)   →   Phase 3: Platform Engineering (21-30)
Linux, Docker, CI, TF, K8s        GitOps, Helm, Secrets, Mesh, Tracing      IDP, eBPF, FinOps, Supply Chain, Zero-Trust
```

---

## 📁 Repository Structure

```
devops-projects/
├── project-01-linux-and-git/          # to project-10-monitoring/
├── project-11-gitops-argocd/          # to project-20-database-backup-restore/
├── project-21-argonaut-gitops/        # to project-30-gitops-db-migrations/
├── docs/
│   ├── learning-roadmap.md
│   ├── interview-questions.md
│   ├── troubleshooting.md
│   └── prerequisites.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Phase 1: Beginner — DevOps Complete Starter (Projects 1-10)
**Goal:** Build fundamentals. A small FastAPI app → Containerized → CI → Cloud → K8s → Monitored.

Project 10 is the capstone — it contains the full app, Docker, Compose, Nginx, CI, deploy workflow, Terraform, K8s, and monitoring in one place.

| # | Project | What It Adds | Core Skills |
|---|---------|--------------|-------------|
| 1 | **project-01-linux-and-git** | Linux server basics, Git workflow | Linux, Bash, Git |
| 2 | **project-02-python-app** | A small FastAPI app | Python, FastAPI, Uvicorn |
| 3 | **project-03-testing** | Automated tests with pytest | pytest, CI testing |
| 4 | **project-04-dockerize** | Packaging the app into a Docker image | Dockerfile, Multi-stage build |
| 5 | **project-05-compose-and-nginx** | Docker Compose + Nginx reverse proxy | Compose, Nginx, Networking |
| 6 | **project-06-ci-github-actions** | Automated testing & building on every push | GitHub Actions, YAML |
| 7 | **project-07-deploy-workflow** | A manual deploy workflow template | GitHub Actions, SSH Deploy |
| 8 | **project-08-terraform-aws** | Provisioning a real AWS server with Terraform | Terraform, AWS EC2/VPC |
| 9 | **project-09-kubernetes** | Running the app under Kubernetes | K8s, Manifests, kubectl |
| 10 | **project-10-monitoring** | Prometheus + Grafana monitoring | Prometheus, Grafana, Metrics |

**Run any project:**
```bash
cd project-04-dockerize/
docker build -t devops-app .
docker run -p 8000:8000 devops-app
```

## Phase 2: Intermediate — Real-World Infra (Projects 11-20)
**Goal:** Move from "it works" to "it works in production". Assumes you have Project 10 running.

| # | Project | What It Adds | Core Skills |
|---|---------|--------------|-------------|
| 11 | **project-11-gitops-argocd** | GitOps deployment with ArgoCD | ArgoCD, GitOps, Kustomize |
| 12 | **project-12-terraform-multi-env** | Terraform modules + remote state (dev/staging/prod) | Terraform Modules, S3 Backend |
| 13 | **project-13-helm-chart** | Packaging the app as a Helm chart | Helm, Charts, Values |
| 14 | **project-14-ingress-tls-autoscaling** | Ingress, automated TLS, and autoscaling | NGINX Ingress, cert-manager, HPA |
| 15 | **project-15-blue-green-canary** | Blue-green / canary deployments | Argo Rollouts, Progressive Delivery |
| 16 | **project-16-centralized-logging** | Centralized logging with Loki + Grafana | Loki, Promtail, LogQL |
| 17 | **project-17-secrets-management** | Secrets management with Vault | HashiCorp Vault, External Secrets |
| 18 | **project-18-service-mesh** | Service mesh basics with Istio | Istio, mTLS, Traffic Management |
| 19 | **project-19-distributed-tracing** | Distributed tracing with OpenTelemetry + Jaeger | OpenTelemetry, Jaeger, Tracing |
| 20 | **project-20-database-backup-restore** | Stateful database with automated backup/restore | Postgres, StatefulSets, Velero |

**Prerequisites for this phase:** `docs/prerequisites.md` — Docker, kubectl, Helm, Terraform, ArgoCD CLI installed.

## Phase 3: Advance — Platform Engineering (Projects 21-30)
**Goal:** Upgraded bundle. Each project is now runnable. Build an Internal Developer Platform.

| # | Project | What It Is | Key Command | Tech Stack |
|---|---------|------------|-------------|------------|
| 21 | **Argonaut GitOps** | Production GitOps bootstrap with App-of-Apps | `make bootstrap` | ArgoCD, Terraform, EKS |
| 22 | **IDP Lite** | Internal Developer Platform portal | `yarn install && yarn dev` | Backstage / Next.js, IDP |
| 23 | **ObserverX eBPF** | Deep observability with eBPF | `docker-compose up` | eBPF, Cilium, Hubble, Grafana |
| 24 | **Kube Economizer** | Kubernetes cost optimization & FinOps | `terraform apply` | Karpenter, Kubecost, HPA/VPA |
| 25 | **Secured Supply Chain** | SLSA + Sigstore + SBOM pipeline | `make scan` | Trivy, Cosign, Syft, Grype |
| 26 | **Terra Orchestrator** | Multi-env Terragrunt orchestration | `terragrunt run-all apply` | Terragrunt, Terraform Cloud |
| 27 | **Auto Heal Bot** | Self-healing infra with Lambda + EventBridge | `make zip && terraform apply` | AWS Lambda, Python, CloudWatch |
| 28 | **Ephemeral PR** | Preview envs per Pull Request | `git push PR` | GitHub Actions, Helm, K8s Namespaces |
| 29 | **Zero Trust Mesh** | Zero Trust with SPIFFE/SPIRE + Istio | `make install` | Istio, SPIRE, mTLS, OPA |
| 30 | **GitOps DB Migrations** | Automated, versioned DB migrations | `atlas migrate apply` | Atlas, ArgoCD, Postgres |

---

### 🛠️ Full Tech Stack Covered

**Languages:** Python, Bash, YAML, HCL, TypeScript
**Containers:** Docker, Docker Compose, Kubernetes, Helm, Kustomize
**CI/CD & GitOps:** GitHub Actions, Jenkins, ArgoCD, Argo Rollouts
**IaC:** Terraform, Terragrunt, Ansible
**Cloud & Scaling:** AWS (EKS, EC2, VPC, S3, Lambda), Karpenter, HPA
**Observability:** Prometheus, Grafana, Loki, OpenTelemetry, Jaeger, eBPF, Cilium
**Security & Platform:** Vault, Trivy, Cosign, Syft, Istio, SPIRE, Backstage

### 🚀 How To Use This Repo

Go in order — each README says what it assumes you already have. Or jump directly to any topic.

```bash
# Clone
git clone https://github.com/karthikbilaspur/ai_learning.git
cd ai_learning/devops-projects

# Pick a project
cd project-08-terraform-aws
cat README.md

# Follow its specific runnable command:
# e.g. for Phase 3
make bootstrap
# or
docker-compose up --build
# or
terraform init && terraform apply
```

All projects 1-20 build on the app from **Project 10**. Projects 21-30 are standalone upgraded bundles.

### ✅ Prerequisites

- Docker Desktop, kubectl, Helm, Terraform
- AWS account (Free Tier) + AWS CLI configured
- Node.js + Yarn (for Project 22 IDP Lite)
- `make`, `git`, `terraform`, `terragrunt` for Phase 3

See `docs/prerequisites.md` and `docs/troubleshooting.md` for common fixes.

### 📚 Shared Docs

- `docs/learning-roadmap.md` — Original phase-by-phase roadmap
- `docs/interview-questions.md` — Practice Q&A covering all 30 topics
- `docs/troubleshooting.md` — Fixes for common issues
- `docs/prerequisites.md` — Tools needed for Projects 11-20

### 🎯 Why This Matters for AI Engineering

AI apps need the same pipeline as any prod app: `Code -> Test -> Docker -> CI -> Terraform -> K8s -> GitOps -> Monitored`. This 30-project track is how I ship my RAG Chatbot and Research Agent from `ai_learning/apps/` to production.

### 👤 Author

**Kai Karthik** — Full Stack + AI Engineer, Bangalore
Building production-ready AI systems.

- GitHub: [@karthikbilaspur](https://github.com/karthikbilaspur/ai_learning)
- Focus: Python, FastAPI, Next.js, LangGraph, RAG, DevOps

> ⭐ Star this repo if you're following along — new projects and platform improvements monthly.

### 🤝 Contributing

See `CONTRIBUTING.md`. PRs for fixes, better docs, or cost optimizations are welcome.

### 📄 License

MIT — See `LICENSE`
