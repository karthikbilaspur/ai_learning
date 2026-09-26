# Advance DevOps Starter — Projects 21–30

The final stretch after Beginner (1–10) and Intermediate (11–20). These are
upgraded, "batteries-included" bundles rather than step-by-step tutorials —
each project is a runnable system on its own, kicked off with a single key
command, covering the kind of platform-engineering-grade problems you'd hit
once GitOps, Kubernetes, and CI/CD are already second nature.

| # | Project | Adds | Key Command |
|---|---------|------|--------------|
| 21 | [project-21-argonaut-gitops](project-21-argonaut-gitops/) | Argonaut GitOps — bootstrapped GitOps pipeline | `make bootstrap` |
| 22 | [project-22-idp-lite](project-22-idp-lite/) | IDP Lite — a lightweight internal developer platform | `yarn install && yarn dev` |
| 23 | [project-23-observerx-ebpf](project-23-observerx-ebpf/) | ObserverX eBPF — kernel-level observability | `docker-compose up` |
| 24 | [project-24-kube-economizer](project-24-kube-economizer/) | Kube Economizer — Kubernetes cost optimization | `terraform apply` |
| 25 | [project-25-secured-supply-chain](project-25-secured-supply-chain/) | Secured Supply Chain — software supply-chain security | `make scan` |
| 26 | [project-26-terra-orchestrator](project-26-terra-orchestrator/) | Terra Orchestrator — multi-stack Terraform orchestration | `terragrunt run-all apply` |
| 27 | [project-27-auto-heal-bot](project-27-auto-heal-bot/) | Auto Heal Bot — automated incident self-healing | `make zip && terraform apply` |
| 28 | [project-28-ephemeral-pr](project-28-ephemeral-pr/) | Ephemeral PR — per-PR ephemeral preview environments | `git push PR` |
| 29 | [project-29-zero-trust-mesh](project-29-zero-trust-mesh/) | Zero Trust Mesh — zero-trust service mesh security | `make install` |
| 30 | [project-30-gitops-db-migrations](project-30-gitops-db-migrations/) | GitOps DB Migrations — GitOps-driven schema migrations | `atlas migrate apply` |

## How to use this

Unlike the Beginner and Intermediate tracks, these aren't meant to be
followed strictly in order — each project is a self-contained, runnable
bundle focused on one advanced platform concern (cost, security, resilience,
observability, multi-cloud orchestration). Pick whichever matches what you
want to practice, `cd` into its folder, and run its key command from the
table above. Each project folder has its own README with setup details and
what it assumes you already have running (typically a working Kubernetes
cluster and the app/cluster built up through Project 10 and the
Intermediate series).

## Prerequisites

- Comfortable with everything from the Beginner and Intermediate tracks (Docker, CI/CD, Terraform, Kubernetes, GitOps, Helm, service mesh)
- Tools vary per project — check each project's own README, but expect a mix of `make`, `yarn`, `docker-compose`, `terraform`, `terragrunt`, and `atlas` depending on which one you're running

## Shared docs

- [../beginner/docs/](../beginner/docs/) and [../intermediate/docs/](../intermediate/docs/) — prerequisites and troubleshooting for the foundations these projects build on
