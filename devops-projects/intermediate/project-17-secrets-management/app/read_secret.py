"""
Minimal example of reading a secret from Vault at startup instead of
from an environment variable or a committed file.

Run this after vault/seed-secret.sh has written the example secret.
"""
import os
import hvac

def get_app_secrets():
    client = hvac.Client(
        url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
        token=os.environ.get("VAULT_TOKEN"),
    )
    if not client.is_authenticated():
        raise RuntimeError("Could not authenticate to Vault")

    result = client.secrets.kv.v2.read_secret_version(path="devops-app")
    return result["data"]["data"]

if __name__ == "__main__":
    secrets = get_app_secrets()
    # Never actually print secrets in real code - this is for the demo only
    print("Fetched keys:", list(secrets.keys()))
