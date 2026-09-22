# Project 5 — Docker Compose & Nginx

Runs the app *and* a reverse proxy together with one command, instead of
managing containers by hand.

## What's here
- `docker-compose.yml` — two services: `app` and `nginx`
- `nginx/nginx.conf` — proxies everything on port 80 to the app container

## What to do

1. Start the stack:
   ```bash
   cp .env.example .env
   docker compose up --build
   ```
2. Visit `http://localhost/`, `http://localhost/health`, and
   `http://localhost/docs` — all through Nginx on port 80 now, not 8000.
3. Stop it:
   ```bash
   docker compose down
   ```

## Concepts to know before moving on
- Why the app container uses `expose` (internal-only) instead of `ports`
  (published to your host) — Nginx is the only thing that should be
  reachable from outside
- What a reverse proxy does, and why you'd put one in front of an app
- Docker Compose's internal DNS (`nginx.conf` refers to the app as
  `app:8000`, not `localhost:8000`)

Next: **Project 6 — CI with GitHub Actions**
