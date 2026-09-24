# Project 20 — A Stateful Database with Backup/Restore Automation

Every previous project's app has been stateless — kill a pod, a new one
starts with no data lost. This project adds a real database with
persistent storage, plus scheduled backups and an actual restore drill,
because "we have backups" doesn't count until you've proven you can
restore from one.

## What's here
- `k8s/postgres-statefulset.yaml` — Postgres as a `StatefulSet` with a
  `PersistentVolumeClaim`, so data survives a pod restart (unlike a plain
  Deployment)
- `k8s/postgres-service.yaml` — a headless Service (`clusterIP: None`),
  which is what StatefulSets need for stable per-pod networking
- `k8s/backup-cronjob.yaml` — runs `pg_dump` every night at 02:00, gzips
  it, and keeps only the last 7 backups
- `k8s/backup-pvc.yaml` — separate storage just for backups, so a disk
  failure on the database volume doesn't also take out its backups
- `restore.sh` — a script that actually performs a restore from a backup
  file, with a confirmation prompt

## What to do

1. Apply everything:
   ```bash
   kubectl apply -f k8s/
   ```
2. Connect and put some real data in:
   ```bash
   kubectl run psql-client --rm -i --tty --restart=Never -n devops-starter \
     --image=postgres:17-alpine -- psql -h postgres -U devops devops_starter
   ```
   ```sql
   CREATE TABLE notes (id serial PRIMARY KEY, body text);
   INSERT INTO notes (body) VALUES ('this should survive a restore drill');
   ```
3. Trigger the backup manually instead of waiting for 2am:
   ```bash
   kubectl create job --from=cronjob/postgres-backup manual-backup-1 -n devops-starter
   kubectl logs job/manual-backup-1 -n devops-starter
   ```
4. **The important part — actually break something and restore it.**
   Delete the `notes` table, then run `restore.sh` with the backup
   filename from step 3's logs:
   ```bash
   ./restore.sh backup-20260101-020000.sql.gz
   ```
5. Reconnect with `psql` and confirm your data is back.

## Concepts to know before moving on
- StatefulSet vs. Deployment — stable identity and storage per pod, at the
  cost of more complexity (this is why every earlier project used a plain
  Deployment for the stateless app)
- Why backups live on a *separate* PVC from the database's own data
- The only backup that counts is one you've tested restoring — step 4
  above is the actual point of this project, not step 3
- In a real cloud setup, you'd likely use a managed database (RDS via
  Terraform) instead of running Postgres in-cluster — this project shows
  the mechanics that a managed service would otherwise hide from you

## You've now covered
GitOps → multi-environment IaC → Helm packaging → ingress/TLS/autoscaling
→ progressive delivery → centralized logging → secrets management →
service mesh → distributed tracing → stateful data with real backup
drills. Combined with the beginner series, that's a genuinely full
end-to-end DevOps skillset, project by project.
