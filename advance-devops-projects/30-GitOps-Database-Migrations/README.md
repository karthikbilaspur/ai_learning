# 30 - GitOps Database Migrations
DB schema versioned in Git, applied by ArgoCD Job + Atlas

Flow: git push atlas/ -> GH Action atlas-action verifies -> ArgoCD syncs Job -> Job runs atlas migrate apply
