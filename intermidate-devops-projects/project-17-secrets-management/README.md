# Project 17 — Secrets Management with Vault

Every project so far has put credentials in `.env` files or plain
Kubernetes Secrets (which are only base64-encoded, not encrypted). This
project runs HashiCorp Vault so secrets are stored encrypted and fetched
at runtime instead of baked into config.

## What's here
- `docker-compose.yml` — Vault in **dev mode** (in-memory, auto-unsealed —
  fine for learning, never for production) + the app
- `vault/seed-secret.sh` — writes an example secret into Vault's key-value
  store
- `app/read_secret.py` — a small script showing the app fetching that
  secret from Vault at runtime, instead of reading it from an env var
- `k8s/sealed-secret-example.yaml` — a second, lighter-weight approach
  (Bitnami Sealed Secrets): encrypt a secret so it's safe to commit to Git,
  and only the in-cluster controller can decrypt it

## What to do

1. Start Vault and the app:
   ```bash
   docker compose up --build -d
   ```
2. Seed the example secret:
   ```bash
   bash vault/seed-secret.sh
   ```
3. Open the Vault UI at `http://localhost:8200` (token: `devroot`) and look
   at `secret/devops-app` — see the values you just wrote.
4. Run the example reader script to fetch it programmatically:
   ```bash
   pip install hvac
   VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=devroot python app/read_secret.py
   ```
5. Compare that to `k8s/sealed-secret-example.yaml` — read the comment at
   the top explaining how you'd generate one for real with `kubeseal`, if
   you have a cluster with the Sealed Secrets controller installed.

## Concepts to know before moving on
- Why a plain Kubernetes `Secret` (base64, not encrypted) isn't actually
  secret if someone can read the cluster's etcd
- Vault's dev mode vs. a real deployment (auto-unseal + root token
  printed in logs is a dev-only shortcut — real Vault requires an unseal
  process and proper auth methods)
- "Encrypt so it's safe to commit" (Sealed Secrets) vs. "fetch at runtime
  from a secret store" (Vault) — two different strategies for the same
  problem

Next: **Project 18 — Service Mesh Basics with Istio**
