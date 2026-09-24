# 21 - Argonaut GitOps CD Engine
Canary + Analysis + Auto Rollback with Argo Rollouts & ArgoCD.

Run: make bootstrap && make deploy

Flow: Git Push -> GH Actions builds & signs -> ArgoCD syncs -> Rollout 20% -> Analysis -> Promote/Rollback
