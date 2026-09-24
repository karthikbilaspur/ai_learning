# Project 4 — Dockerize the App

Packages Project 3's app and tests into a container image, so it runs the
same way on any machine.

## What's here
- `Dockerfile` — Python 3.12-slim base, installs deps, runs uvicorn on 8000
- `.dockerignore` — keeps the build context small
- Same `app/`, `tests/`, `requirements.txt` as Project 3

## What to do

1. Build the image:
   ```bash
   docker build -t devops-starter:local .
   ```
2. Run it directly (without Compose or Nginx yet):
   ```bash
   docker run --rm -p 8000:8000 devops-starter:local
   ```
3. Visit `http://localhost:8000/health`.
4. Look at the image's layers:
   ```bash
   docker history devops-starter:local
   ```

## Concepts to know before moving on
- The difference between an image and a running container
- Why `.dockerignore` matters (try removing it and compare build context
  size with `docker build --progress=plain`)
- What `EXPOSE` does and doesn't do (it's documentation, not a firewall rule)

Next: **Project 5 — Docker Compose & Nginx**
