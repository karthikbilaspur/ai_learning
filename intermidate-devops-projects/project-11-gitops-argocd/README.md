# Project 11 — GitOps Deployment with ArgoCD

Up to now you've deployed to Kubernetes by running `kubectl apply -f k8s/`
by hand (Project 9). GitOps flips that: Git becomes the single source of
truth, and a controller (ArgoCD) keeps the cluster in sync with it
automatically — no more manual `kubectl apply`.

## What's here
- `k8s/` — the same manifests style as Project 9's, treated as the "desired
  state" ArgoCD will enforce
- `argocd/application.yaml` — an ArgoCD `Application` pointing at this
  repo/path, with automated sync and self-healing turned on

## Assumes
A Kubernetes cluster (Minikube is fine) and this folder pushed to a Git
repo ArgoCD can reach.

## What to do

1. Install ArgoCD into your cluster:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```
2. Port-forward the ArgoCD UI and log in (see ArgoCD's docs for the initial
   admin password):
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```
3. Edit `argocd/application.yaml` — point `repoURL` at your own fork of
   this repo — then apply it:
   ```bash
   kubectl apply -f argocd/application.yaml
   ```
4. Watch ArgoCD sync `k8s/` into the `devops-starter` namespace
   automatically, either in the UI or with:
   ```bash
   kubectl get application devops-starter -n argocd
   ```
5. Try the "self-heal" behavior: manually edit the deployment with
   `kubectl edit deployment devops-app -n devops-starter` (e.g. change the
   replica count), then watch ArgoCD revert it back to what's in Git.
6. Make a real change: edit `k8s/deployment.yaml` in Git (e.g. bump
   `replicas` to 3), commit, push, and watch ArgoCD pick it up without you
   touching `kubectl` at all.

## Concepts to know before moving on
- "Desired state in Git, cluster state converges to it" — the core GitOps
  idea
- `selfHeal` vs `prune`: healing reverts drift, pruning deletes resources
  removed from Git
- Rolling back a bad deploy is just `git revert`, not a `kubectl` command

Next: **Project 12 — Multi-Environment Terraform**
