# Prerequisites for the Intermediate Series

Not every project needs every tool — each project's README says exactly
what it uses — but across all 10 you'll want:

- A running Kubernetes cluster (Minikube is fine for most of these; a
  real cloud cluster is better for Projects 11, 12, 14, and 20)
- `kubectl` and `helm` installed
- `terraform` installed, plus an AWS (or other cloud) account for
  Projects 12 and 20
- A GitHub account (Projects 11 and 15 use a Git repo as their source of
  truth / deploy trigger)
- Docker and Docker Compose, for the projects that run supporting infra
  locally instead of in the cluster (16, 17, 19)

Where a project needs a paid cloud resource (an RDS instance, a real
domain for TLS), the README says so up front and gives a local
alternative where one exists.
