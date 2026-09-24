#!/usr/bin/env bash
# Run this once Vault is up, to store an example secret the app can read.
set -euo pipefail

export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=devroot

vault kv put secret/devops-app \
  api_key="example-super-secret-key" \
  db_password="example-not-a-real-password"

echo "Secret written to secret/devops-app"
