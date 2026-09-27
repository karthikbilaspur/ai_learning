Here is the cleaned, standalone professional version — no mention of Beginner / Intermediate:

```markdown
# Advanced DevOps Starter — Projects 21–30

> Production-shaped, batteries-included systems for platform engineering problems. Each project is a runnable system on its own, kicked off with a single key command.

These are not step-by-step tutorials. Each project is a self-contained reference implementation built around one advanced platform concern — cost optimization, security, resilience, observability, and multi-cloud orchestration — designed to run as a complete system.

## 🧠 What You'll Build

This track covers the real platform problems you hit at scale:

- **GitOps at Scale:** Bootstrapped GitOps pipelines and Internal Developer Platforms
- **Deep Observability:** Kernel-level observability with eBPF
- **FinOps:** Kubernetes cost optimization and reporting
- **Security:** Supply-chain security and Zero-Trust service mesh
- **Resilience & DX:** Self-healing automation, Ephemeral PR environments, GitOps-driven DB migrations
- **Multi-Cloud Orchestration:** Multi-stack Terraform management with Terragrunt

## 📋 Prerequisites

Check `docs/` for exact tool versions for this track. At a minimum you should have:

- Docker + Docker Compose
- Kubernetes cluster (kind / k3d / EKS / GKE) with `kubectl` access
- Helm v3.12+, Terraform v1.5+, Terragrunt
- Node.js / Yarn, Make, Git
- A cloud account (AWS / GCP) for projects that provision real resources

> ⚠️ Several projects provision real cloud resources. Read `docs/` for cost and teardown warnings before running any `terraform apply`.

## 🚀 The 10 Capstones

Each project is runnable with a single key command, but always read its own README first to understand what it does under the hood.

| # | Project | Adds | Key Command |
| :--- | :--- | :--- | :--- |
| **21** | [project-21-argonaut-gitops](project-21-argonaut-gitops/) | **Argonaut GitOps** — bootstrapped GitOps pipeline | `make bootstrap` |
| **22** | [project-22-idp-lite](project-22-idp-lite/) | **IDP Lite** — lightweight internal developer platform | `yarn install && yarn dev` |
| **23** | [project-23-observerx-ebpf](project-23-observerx-ebpf/) | **ObserverX eBPF** — kernel-level observability | `docker-compose up` |
| **24** | [project-24-kube-economizer](project-24-kube-economizer/) | **Kube Economizer** — Kubernetes cost optimization | `terraform apply` |
| **25** | [project-25-secured-supply-chain](project-25-secured-supply-chain/) | **Secured Supply Chain** — software supply-chain security | `make scan` |
| **26** | [project-26-terra-orchestrator](project-26-terra-orchestrator/) | **Terra Orchestrator** — multi-stack Terraform orchestration | `terragrunt run-all apply` |
| **27** | [project-27-auto-heal-bot](project-27-auto-heal-bot/) | **Auto Heal Bot** — automated incident self-healing | `make zip && terraform apply` |
| **28** | [project-28-ephemeral-pr](project-28-ephemeral-pr/) | **Ephemeral PR** — per-PR ephemeral preview environments | `git push` (on PR) |
| **29** | [project-29-zero-trust-mesh](project-29-zero-trust-mesh/) | **Zero Trust Mesh** — zero-trust service mesh security | `make install` |
| **30** | [project-30-gitops-db-migrations](project-30-gitops-db-migrations/) | **GitOps DB Migrations** — GitOps-driven schema migrations | `atlas migrate apply` |

## 🛠️ How to Use This

**1. Pick by problem, not by order.**
There is no dependency chain. Each project is its own upgraded, self-contained bundle. Jump to whichever concept you want to practice.

**2. Read the project's README first.**
Even though the top-level command is short, each folder's README spells out what it assumes you have installed, what exactly the key command does, and how to verify it.

**3. Treat these as capstones, not tutorials.**
These are closer to production-shaped reference implementations than guided lessons — expect to read code, not just follow steps.

Example workflow:
```bash
cd project-21-argonaut-gitops/
cat README.md

make bootstrap
./scripts/verify.sh

# When done
make teardown
```

## 📁 Repository Structure

```
.
├── docs/                               # Tool versions, cluster setup, cost/teardown notes
├── project-21-argonaut-gitops/
│   ├── README.md
│   ├── manifests/ | terraform/ | app/
│   └── Makefile
├── ...
├── project-30-gitops-db-migrations/
├── CONTRIBUTING.md
└── LICENSE
```

## ⚠️ Cost & Teardown Warning

Projects 24, 26, 27, and 28 provision cloud resources (EKS/GKE, S3, IAM, Lambda, Cloud Run). Always run `terraform destroy` or `terragrunt run-all destroy` when finished and check `docs/` for specific cleanup steps.

## 🤝 Contributing

Found a better pattern or optimization? PRs and issues are welcome. Please open an issue first for major changes.

---
**Start here:** [Project 21 - Argonaut GitOps](project-21-argonaut-gitops/) to bootstrap your platform.
```
