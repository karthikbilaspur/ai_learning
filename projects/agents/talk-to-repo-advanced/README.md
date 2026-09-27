# Talk-To-Repo — Advanced

Point it at a public GitHub/GitLab/Bitbucket repo and ask questions about
the codebase. Answers are grounded in retrieved code, cite `file:line`,
and can pull in a call-graph view of how the cited functions relate.

## What it actually does

1. **AST-aware chunking** — tree-sitter parses JS/TS/Python and chunks by
   function/class instead of fixed-size text windows, so retrieved context
   is a complete function, not an arbitrary 800-token slice. Falls back to
   a text splitter for unsupported file types.

2. **Hybrid search + reranking** — vector search (SentenceTransformers +
   Chroma) and BM25 keyword search run in parallel and are merged, then a
   cross-encoder (`ms-marco-MiniLM-L-6-v2`) reranks the top candidates
   down to the 5 used for context.

3. **Call graph** — built by tree-sitter while chunking: every
   function/class definition becomes a node, and every call site is
   matched by name to definitions anywhere in the repo. **This is a
   name-based heuristic, not a scope/type resolver** — if two files each
   define a function called `handle`, a call to `handle()` links to both.
   For most single-repo codebases with reasonably distinct names this is a
   useful signal; it is not a substitute for a real language-server-grade
   call graph. `GET /callers?repo_id=&function=` answers "what calls this"
   directly from the graph, no LLM involved.

4. **Bounded agentic loop** — the model can end a response with
   `NEED_MORE: <file>` to request the full contents of one more file
   before finalizing its answer. The backend actually parses that,
   fetches the file (through the same path-safety check as `/read-file`),
   and re-prompts with the extra context — capped at 2 extra passes so a
   confused model can't loop forever.

5. **Exact citations + file viewer** — answers cite `file:line`; clicking
   a citation fetches the real file content via `/read-file` and shows it
   in a read-only Monaco editor.

Stack: FastAPI, tree-sitter, ChromaDB (persistent), SentenceTransformers +
CrossEncoder, Ollama (codellama), GitPython, rank-bm25. Frontend: Vite +
React + Monaco + React Flow (call graph) + react-markdown.

## Setup

```bash
ollama pull codellama:13b
ollama pull nomic-embed-text   # optional, better code embeddings

cd backend-python
python -m venv .venv
# activate the environment
pip install -r requirements.txt
python -m app.core.install_treesitter   # downloads grammars
cp .env.example .env
uvicorn app.main:app --port 8000 --reload
```

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## API

- `POST /ingest {repo_url}` — clone + index a repo. `repo_url` must be an
  `https://` URL on github.com, gitlab.com, or bitbucket.org (see
  Security below for why).
- `POST /query/stream {repo_id, question}` — SSE stream of `token`,
  `citations`, and `graph` events.
- `GET /read-file?repo_id=&path=` — read a file from the cloned repo.
- `GET /call-graph?repo_id=` — the full call graph for a repo.
- `GET /callers?repo_id=&function=` — who calls a given function name.

## Security notes

- **`repo_url` is restricted to `https://github.com|gitlab.com|bitbucket.org`.**
  Cloning an arbitrary server-side URL from user input is a real SSRF /
  command-injection surface (malicious git transports like `ext::`,
  URLs pointed at internal services). An allowlist of known public git
  hosts over plain HTTPS closes that off. Loosen it deliberately, not by
  accident, if you need to support self-hosted git servers.
- **`/read-file` resolves paths with `os.path.realpath` + containment
  check**, not a naive `startswith()` on an unnormalized path (the
  original version of this had a directory-traversal bug where
  `../../etc/passwd` would pass the check as a string while still
  resolving outside the sandbox).
- **CORS is restricted** to `ALLOWED_ORIGINS` (defaults to the Vite dev
  origin), not `*`.
- **`trust_remote_code=True`** is used to load the `nomic-embed-text`
  embedding model, which executes custom Python shipped in that
  HuggingFace repo. That's a real supply-chain trust decision — it falls
  back to a safe, no-custom-code model (`all-MiniLM-L6-v2`) if that's not
  acceptable for your environment.
- Cloned repos and uploaded question text are not otherwise sandboxed —
  this is a local dev tool, not something to expose on the open internet
  as-is.

## Known limitations

- The call graph is name-based, not scope-resolved (see above) — treat it
  as "likely related", not ground truth, especially in codebases with
  common method names like `run`, `handle`, `execute`.
- The agentic loop is capped at 2 extra file-read passes.
- Only `.js/.ts/.jsx/.tsx/.py` get AST-aware chunking; other text files
  fall back to naive splitting.
- Files over 20,000 characters are skipped during ingestion.
- No persistence of chat history between questions — each question is
  answered independently against the indexed repo.
