# DevOps Complete Starter — 10 Projects From Zero to Production

A progressive DevOps portfolio designed for beginners. 10 standalone projects, each adds exactly one new concept — from Linux basics to Prometheus & Grafana monitoring.

> Each folder is self-contained with its own README, code, and instructions. Go in order 1 → 10, or jump to any topic.

[[Linux](https://img.shields.io/badge/Linux-Ubuntu-orange?logo=linux)]()
[[Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)]()
[[Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5?logo=kubernetes)]()
[[Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform)]()
[[CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-black?logo=githubactions)]()

## Architecture Progression

```
Project 01: Linux + Git
    ↓
Project 02: FastAPI App (Python)
    ↓
Project 03: pytest
    ↓
Project 04: Docker
    ↓
Project 05: Docker Compose + Nginx (Reverse Proxy)
    ↓
Project 06: CI with GitHub Actions (Test + Build)
    ↓
Project 07: CD - Manual Deploy Workflow
    ↓
Project 08: Terraform + AWS EC2
    ↓
Project 09: Kubernetes (Deployment + Service)
    ↓
Project 10: Monitoring (Prometheus + Grafana) — FULL STACK
```

## Projects

| # | Project | What You Learn | Key Tools |
|---|---------|----------------|-----------|
| **01** | [project-01-linux-and-git](project-01-linux-and-git/) | Linux server basics, file system, permissions, Git workflow | Ubuntu, Bash, Git |
| **02** | [project-02-python-app](project-02-python-app/) | Build a production-ready API | Python, FastAPI, Uvicorn |
| **03** | [project-03-testing](project-03-testing/) | Automated testing & test coverage | pytest, pytest-cov |
| **04** | [project-04-dockerize](project-04-dockerize/) | Packaging app into optimized Docker image | Docker, Multi-stage build |
| **05** | [project-05-compose-and-nginx](project-05-compose-and-nginx/) | Multi-container orchestration + reverse proxy | Docker Compose, Nginx |
| **06** | [project-06-ci-github-actions](project-06-ci-github-actions/) | CI pipeline on every push | GitHub Actions, Docker Buildx |
| **07** | [project-07-deploy-workflow](project-07-deploy-workflow/) | Manual deployment workflow, environments | GitHub Actions, SSH, Deploy |
| **08** | [project-08-terraform-aws](project-08-terraform-aws/) | Infrastructure as Code on real cloud | Terraform, AWS EC2, VPC |
| **09** | [project-09-kubernetes](project-09-kubernetes/) | Running workloads in K8s | Kubernetes, kubectl, K8s Manifests |
| **10** | [project-10-monitoring](project-10-monitoring/) | Observability & monitoring | Prometheus, Grafana, Alerting |

## How to Use

**Recommended path (beginner):**
```bash
# Clone
git clone <your-repo-url>
cd devops-starter

# Start with Project 01
cd project-01-linux-and-git
cat README.md
```

**Jump to any topic:**
Each folder is independent. Want to practice only Kubernetes?
```bash
cd project-09-kubernetes/
# Follow its README
```

**Finished version:**
`project-10-monitoring/` contains everything — app + Docker + Compose + Nginx + CI + Deploy + Terraform + Kubernetes + Monitoring. Treat it as the final production setup.

## Prerequisites

- Git, Docker Desktop, Python 3.10+
- For Project 08: AWS account + AWS CLI configured
- For Project 09: minikube or kind, or any K8s cluster
- Basic command line knowledge

## Learning Path

**Phase 1 — Fundamentals (01-03):** OS, Git, App, Testing
**Phase 2 — Containerization (04-05):** Docker, Compose, Nginx
**Phase 3 — Automation (06-07):** CI/CD
**Phase 4 — Cloud & Scale (08-10):** IaC, Kubernetes, Monitoring

Detailed roadmap: [docs/learning-roadmap.md](docs/learning-roadmap.md)

## Shared Documentation

- [docs/learning-roadmap.md](docs/learning-roadmap.md) — Phase-by-phase roadmap
- [docs/interview-questions.md](docs/interview-questions.md) — 100+ DevOps interview Q&A covering all 10 topics
- [docs/troubleshooting.md](docs/troubleshooting.md) — Common errors and fixes for every project
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)

## What You Will Be Able To Do After Project 10

- Provision infrastructure with Terraform on AWS
- Containerize and run apps with Docker & Compose behind Nginx
- Automate build/test/deploy with GitHub Actions
- Deploy to Kubernetes
- Monitor with Prometheus + Grafana dashboards

---

If this helps, give it a ⭐ — helps others find it.
