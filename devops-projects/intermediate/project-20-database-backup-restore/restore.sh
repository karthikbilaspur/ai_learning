#!/usr/bin/env bash
# Restore a backup produced by the CronJob. Run from your local machine
# with kubectl configured against the cluster.
#
# Usage: ./restore.sh backup-20260101-020000.sql.gz
set -euo pipefail

BACKUP_FILE="${1:?Usage: ./restore.sh <backup-filename>}"
NAMESPACE=devops-starter

echo "This will DROP and recreate data in the devops_starter database."
read -p "Type 'restore' to continue: " CONFIRM
[ "$CONFIRM" = "restore" ] || { echo "Aborted."; exit 1; }

# Copy the backup out of the PVC via a temporary pod, then pipe it into psql
kubectl run restore-helper --rm -i --tty --restart=Never -n "$NAMESPACE" \
  --image=postgres:17-alpine \
  --overrides='{"spec":{"containers":[{"name":"restore-helper","image":"postgres:17-alpine","stdin":true,"tty":true,"volumeMounts":[{"name":"backups","mountPath":"/backups"}]}],"volumes":[{"name":"backups","persistentVolumeClaim":{"claimName":"postgres-backups"}}]}}' \
  -- sh -c "gunzip -c /backups/$BACKUP_FILE | psql -h postgres -U devops devops_starter"

echo "Restore attempted. Verify your data before trusting it."
