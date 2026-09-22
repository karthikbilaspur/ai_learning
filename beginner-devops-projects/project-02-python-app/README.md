# Project 2 — Python App Basics

A small FastAPI app that every later project builds, ships, and monitors.

## What's here
- `app/main.py` — three endpoints: `/`, `/health`, `/api/info`
- `requirements.txt` — dependencies
- `.env.example` — the environment variables the app (and later, Docker
  Compose) reads

## What to do

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy the env file and run the app directly:
   ```bash
   cp .env.example .env
   uvicorn app.main:app --reload
   ```
3. Visit `http://localhost:8000/`, `http://localhost:8000/health`, and
   `http://localhost:8000/docs` (FastAPI's auto-generated API docs).

## Concepts to know before moving on
- What a web framework does vs. a plain script
- Environment variables and why they're not hardcoded into code
- What `/health` endpoints are for (you'll see this used again by Docker
  and Kubernetes health checks in later projects)

Next: **Project 3 — Testing the App**
