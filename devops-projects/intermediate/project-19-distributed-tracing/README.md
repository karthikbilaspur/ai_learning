# Project 19 — Distributed Tracing with OpenTelemetry + Jaeger

Project 10 gave you metrics (how many requests, how fast on average).
Tracing shows you *one specific request's* full journey — every step it
took and how long each step spent — which is what you actually need when
debugging "why was this one request slow."

## What's here
- `app/main.py` — the same app, instrumented with OpenTelemetry; every
  request auto-generates a trace, and `/api/info` adds a manual child span
  around its slow step
- `otel-collector/otel-collector-config.yml` — receives traces from the
  app over OTLP and forwards them to Jaeger
- `docker-compose.yml` — app + OpenTelemetry Collector + Jaeger

## What to do

1. Start everything:
   ```bash
   docker compose up --build
   ```
2. Hit the app a few times, including the slower endpoint:
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/api/info
   curl http://localhost:8000/api/info
   ```
3. Open the Jaeger UI at `http://localhost:16686`, select `devops-app` as
   the service, and click **Find Traces**.
4. Open one of the `/api/info` traces — you'll see the outer HTTP span and,
   nested inside it, the `build-info-payload` span showing exactly how
   long that manual step took.
5. Compare a few `/api/info` traces' durations against each other — since
   the code sleeps a random amount, you should see the variation directly
   in the trace timeline, not just as an average.

## Concepts to know before moving on
- Span vs. trace: a trace is the whole request's journey; a span is one
  step within it (and spans can nest, like `build-info-payload` inside the
  HTTP request span)
- Auto-instrumentation (FastAPI's HTTP spans, free) vs. manual
  instrumentation (the `tracer.start_as_current_span` call, for things the
  library can't see on its own)
- Why this app didn't need code changes to talk to Jaeger directly — it
  only knows about the OpenTelemetry Collector, which is what actually
  exports to a specific backend. Swapping Jaeger for another backend later
  means editing the collector's config, not the app.

Next: **Project 20 — A Stateful Database with Backup/Restore**
