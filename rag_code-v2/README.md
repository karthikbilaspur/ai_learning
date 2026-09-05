# Production RAG Agent v5

A hardened RAG reference implementation with hybrid retrieval, optional CrossEncoder reranking, grounded LLM generation, safe calculator tooling, request IDs, rate limiting, structured tracing, evaluation gates, and Docker deployment.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export LLM_PROVIDER=mock
uvicorn api.main:app --reload
```

For OpenAI generation, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY`.

Run tests with `pytest -q` and evaluation with `python -m evals.run_eval`.

## Production notes
- Index construction is performed once during application startup instead of once per request.
- User-provided tool expressions are parsed through a strict AST allow-list; no `eval`/`exec`.
- Pydantic models reject unexpected API/tool fields.
- LLM prompts explicitly separate untrusted retrieved data from system instructions.
- The API does not return raw exception messages to clients.
- Rate limiting and traces are process-local; for multi-instance deployment, replace them with Redis/OpenTelemetry.
- Retrieval indexes are persisted under `data/index` (FAISS + embeddings for dense mode, or TF-IDF artifacts in fallback mode) and are reused when the document/chunk fingerprint and embedding model match. Set `FORCE_REBUILD_INDEX=true` to rebuild explicitly.
- Evaluation heuristics remain smoke tests, not proof of factual faithfulness. Add an LLM judge/RAGAS-style pipeline before using metrics as a release gate.

## API
`POST /query`, `GET /health`, `GET /ready`, `GET /metrics`
