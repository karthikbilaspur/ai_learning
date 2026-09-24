#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl docker.io docker-compose-plugin

sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

echo "Docker installed. Log out/in for docker group changes to take effect."
echo "Clone the project and run: docker compose up -d --build"
