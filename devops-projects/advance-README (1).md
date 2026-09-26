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

This track is different in shape from Beginner and Intermediate. Those two
walk you through one new concept at a time, in order, on top of the same
running app. Here, each project is its own upgraded, self-contained bundle —
a runnable system built around a single advanced platform concern (cost,
security, resilience, observability, multi-cloud orchestration), rather than
another step in a shared build-up.

That means:

- **You don't need to go in order.** Pick whichever project matches the
  concept you want to practice — there's no dependency chain like there is
  in the earlier two tracks.
- **Each project stands alone.** `cd` into its folder and run its key
  command from the table above (`make bootstrap`, `terraform apply`,
  `docker-compose up`, etc.) — no shared app or cluster state is required
  between projects.
- **Read the project's own README first.** Even though the top-level
  command is short, each folder's README spells out what it assumes you
  already have installed or running, and what exactly the key command does
  under the hood.
- **Treat these as capstones, not tutorials.** They're closer to
  "production-shaped" reference implementations of a specific pattern
  (GitOps bootstrapping, eBPF observability, cost optimization, supply-chain
  security, etc.) than a guided lesson — expect to read code, not just
  follow steps.

If you're coming from the Intermediate track, Projects 11–20 already gave
you the underlying skills (GitOps, Helm, ingress/autoscaling, logging,
secrets, service mesh, tracing) that these advanced bundles assume and build
further on.

## Shared docs

- [docs/](docs/) — cross-project notes for this track: tool versions, cluster/cloud account setup, and cost or teardown warnings (several of these projects provision real cloud resources, so check this before running `terraform apply` / `terragrunt run-all apply`)
- [../intermediate/docs/prerequisites.md](../intermediate/docs/prerequisites.md) — the underlying tools (Kubernetes, Helm, Terraform, etc.) these projects assume you already have installed
- [../beginner/docs/troubleshooting.md](../beginner/docs/troubleshooting.md) — fixes for the more foundational issues (Docker, Git, basic CI) that can still surface here
- [CONTRIBUTING.md](../beginner/CONTRIBUTING.md) · [LICENSE](../beginner/LICENSE) — shared across all three tracks
