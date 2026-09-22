# Project 10 — Monitoring with Prometheus & Grafana

The final project: the full stack from Projects 1–9, plus metrics and a
dashboard, so you can see what your app is actually doing.

## What's here
- `monitoring/prometheus.yml` — scrapes the app's `/metrics` endpoint
- `monitoring/grafana/provisioning/` — auto-connects Grafana to Prometheus
  on startup (no manual setup needed)
- `docker-compose.yml` — now four services: `app`, `nginx`, `prometheus`,
  `grafana`
- `Makefile` — `make up`, `make down`, `make test`, etc.
- Everything from Projects 1–9 (app, tests, Docker, Nginx, CI, deploy
  template, Terraform, Kubernetes)

## What to do

1. Start the full stack:
   ```bash
   cp .env.example .env
   make up
   ```
   (or `docker compose up --build` if you'd rather not use the Makefile)
2. Generate some traffic by refreshing `http://localhost/` a few times.
3. Open Prometheus at `http://localhost:9090` and query `http_requests_total`.
4. Open Grafana at `http://localhost:3001` (login `admin`/`admin`, or
   whatever you set in `.env`) — Prometheus is already connected as a data
   source. Build a simple dashboard panel showing request count over time.
5. Read `docs/troubleshooting.md` in the project root if anything doesn't
   come up cleanly.

## Concepts to know
- The difference between logs, metrics, and traces (this project only
  covers metrics)
- What a `/metrics` endpoint exposes and how Prometheus scrapes it
- Why Grafana's data source is provisioned as a file instead of clicked
  in through the UI (so it's reproducible)

## You've now covered
Linux & Git → a Python app → tests → Docker → Compose & Nginx → CI →
a deploy workflow → Terraform → Kubernetes → monitoring. That's the same
ground the original `docs/learning-roadmap.md` lays out, project by
project.
