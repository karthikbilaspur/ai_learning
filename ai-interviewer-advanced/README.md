# AI Interviewer Advanced — Full-Stack Dev (Voice + LangGraph)

Practice mock interviews by voice. Pick a role and level, answer out loud,
get scored with specific feedback, and the next question adapts to your
weak spots.

## What's real in this build

- **Question bank**: 48 questions across 4 roles (Fullstack, Frontend,
  Backend, AI Engineer) x 3 levels (Junior, Mid, Senior) — every
  role/level combo in the UI actually has content.
- **LangGraph orchestration**: `interviewer_graph.py` is a real
  `StateGraph` (planner → questioner, or evaluator → planner → questioner,
  routed conditionally). If `langgraph` isn't installed, it falls back to
  a hand-rolled runner with the *identical* node functions and routing —
  not a different, simpler thing pretending to be the same.
- **Adaptive planner**: the next question is chosen by hybrid retrieval
  (BM25 + Chroma vector search, fused with reciprocal rank fusion) against
  your weak categories from memory — not `random.choice()`.
- **Hybrid + rerank retrieval**: BM25 and Chroma vector search are both
  actually queried and fused in `retrieval.py`. Cross-encoder reranking
  runs if `sentence-transformers` + a CrossEncoder model are available;
  otherwise it's skipped and `/status` reports that honestly instead of
  claiming it ran.
- **Session-scoped memory**: SQLite (`/tmp/interviewer_memory.db`) keyed
  by a per-browser session id, not a single shared JSON file that
  collided across every user and tab.
- **Honest failure modes**: if Whisper can't transcribe your audio, the
  API returns a 502 with a real error message — it does not silently
  return a canned fake transcript. If Piper TTS isn't set up, `audio_url`
  is `null` and the frontend genuinely falls back to the browser's
  `SpeechSynthesis` API instead of playing a silent `.wav`.
- **`/status` endpoint**: reports which backends (LangGraph, BM25, Chroma,
  cross-encoder) are actually active for this run. The frontend's "Stack"
  panel reads this instead of hardcoding checkmarks.
- **Eval harness**: `run_evals.py` actually runs the evaluator node
  against `eval_set.json` and checks keyword coverage — it's a keyword
  proxy, not RAGAS, and doesn't claim to be.

## What's still not here

- No auth / multi-tenant isolation beyond the session id in `localStorage`.
- No Langfuse tracing wired up yet (env vars are read but nothing sends
  spans) — added to `requirements.txt` as a clearly-marked next step, not
  claimed as done.
- Cross-encoder rerank needs `sentence-transformers` + model weights,
  which are large; it degrades gracefully without them, but isn't
  guaranteed to be running unless you check `/status`.
- No containerization yet (Docker Compose for Ollama + backend + frontend
  would be the natural next step for reliable setup).

## How it works

1. Pick role (Fullstack / Frontend / Backend / AI Engineer) and level
   (Junior / Mid / Senior).
2. LangGraph's planner node picks a question via hybrid retrieval; Piper
   TTS speaks it (or your browser's TTS if Piper isn't set up).
3. Hold the mic button, answer, release. Whisper transcribes it.
4. The evaluator node scores it via Ollama (`codellama:13b`) — falling
   back to a length-based heuristic, clearly labeled as such, if Ollama
   isn't running.
5. Memory updates per-category strengths/weaknesses in SQLite; the
   planner uses that to pick the next question.

## Run it

```bash
ollama pull codellama:13b   # optional — falls back to heuristic scoring without it
cd backend-python && pip install -r requirements.txt && uvicorn app.main:app --port 8000 --reload
cd frontend && npm install && npm run dev
```

Optional, for the full stack described above:
- `PIPER_VOICE=/path/to/voice.onnx` env var + `pip install piper-tts` for
  real TTS audio instead of browser TTS.
- `sentence-transformers` (already in requirements.txt) for cross-encoder
  reranking — first run downloads model weights.

Run the eval harness:
```bash
cd backend-python && python -m app.evals.run_evals
```
