# Project 16 — Centralized Logging with Loki + Grafana

Project 10 (beginner series) gave you metrics. This project adds logs —
Promtail ships every container's stdout into Loki, and you query and
correlate them in the same Grafana you already have.

## What's here
- `loki/loki-config.yml` — Loki configured with local filesystem storage
  (fine for learning; a real deployment would use object storage)
- `promtail/promtail-config.yml` — discovers Docker containers labeled
  `logging: promtail` and ships their logs to Loki
- `grafana/provisioning/datasources/loki.yml` — auto-connects Grafana to
  Loki, same pattern as Project 10's Prometheus datasource
- `docker-compose.yml` — app + Loki + Promtail + Grafana

## What to do

1. Start everything:
   ```bash
   docker compose up --build
   ```
2. Generate some traffic and a few errors:
   ```bash
   for i in $(seq 1 20); do curl -s http://localhost:8000/ > /dev/null; done
   curl -s http://localhost:8000/does-not-exist
   ```
3. Open Grafana at `http://localhost:3001` (`admin`/`admin`) → **Explore**
   → select the Loki data source → query:
   ```
   {container="devops-app"}
   ```
4. Filter to just the errors:
   ```
   {container="devops-app"} |= "404"
   ```
5. Build a dashboard panel showing log volume over time, and place it next
   to the request-count panel from Project 10 — that's the beginning of
   correlating logs with metrics.

## Concepts to know before moving on
- Why Loki indexes only *labels*, not full log text (unlike Elasticsearch)
  — it's why it's cheaper to run, and why your queries filter on labels
  first
- LogQL basics: `{label="value"}` to select a stream, `|=` to filter text
  within it
- The `logging: promtail` label in `docker-compose.yml` — Promtail only
  picks up containers it's told to, not everything on the host

Next: **Project 17 — Secrets Management with Vault**
