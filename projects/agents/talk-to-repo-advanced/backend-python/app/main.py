"""
FastAPI service: clone a repo, index it (AST chunks + hybrid search + call
graph), then answer questions about it with a bounded agentic RAG loop.
"""

import json
import logging
import os
import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from .core.ingester import find_callers, ingest_repo_advanced, load_call_graph
from .core.paths import safe_repo_path
from .core.rag_advanced import agentic_query_stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("talktorepo.main")

app = FastAPI(title="Talk-to-Repo Advanced Brain")

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Cloning an arbitrary user-supplied git URL server-side is a real SSRF /
# command-injection surface (e.g. the `ext::` git transport, or URLs
# pointed at internal-network services). Restrict to plain https:// URLs
# on known public git hosts rather than trying to blacklist bad schemes.
ALLOWED_GIT_HOSTS = {"github.com", "gitlab.com", "bitbucket.org"}

REPOS: dict[str, dict] = {}  # repo_id -> ingest result
MAX_FILE_READ_CHARS = 20_000


class IngestReq(BaseModel):
    repo_url: str

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme != "https":
            raise ValueError("repo_url must use https://")
        host = (parsed.hostname or "").lower()
        if host not in ALLOWED_GIT_HOSTS:
            raise ValueError(f"repo_url host must be one of {sorted(ALLOWED_GIT_HOSTS)}")
        return value


class QueryReq(BaseModel):
    repo_id: str
    question: str


@app.post("/ingest")
def ingest(req: IngestReq):
    repo_id = str(uuid.uuid4())[:8]
    try:
        result = ingest_repo_advanced(req.repo_url, repo_id)
    except Exception as exc:
        logger.error("Ingest failed for %s: %s", req.repo_url, exc)
        raise HTTPException(status_code=502, detail=f"Failed to clone or index repo: {exc}") from exc

    REPOS[repo_id] = result
    return {"repo_id": repo_id, **result}


@app.post("/query/stream")
def query_stream(req: QueryReq):
    if req.repo_id not in REPOS:
        raise HTTPException(status_code=404, detail="Unknown repo_id. Ingest the repo first.")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty.")

    def gen():
        for event in agentic_query_stream(req.repo_id, req.question):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/read-file")
def read_file(repo_id: str, path: str):
    if repo_id not in REPOS:
        raise HTTPException(status_code=404, detail="Unknown repo_id.")

    resolved = safe_repo_path(repo_id, path)
    if resolved is None:
        # Deliberately vague — don't confirm/deny paths outside the sandbox.
        raise HTTPException(status_code=400, detail="Invalid path.")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        with open(resolved, errors="ignore") as f:
            content = f.read(MAX_FILE_READ_CHARS)
        return {"content": content, "truncated": os.path.getsize(resolved) > MAX_FILE_READ_CHARS}
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/call-graph")
def call_graph(repo_id: str):
    if repo_id not in REPOS:
        raise HTTPException(status_code=404, detail="Unknown repo_id.")
    return load_call_graph(repo_id)


@app.get("/callers")
def callers(repo_id: str, function: str):
    """Answers 'what breaks if I change this function?' directly from the
    static call graph, without going through the LLM."""
    if repo_id not in REPOS:
        raise HTTPException(status_code=404, detail="Unknown repo_id.")
    return {"function": function, "callers": find_callers(repo_id, function)}


@app.get("/")
def health():
    return {
        "status": "Advanced RAG online",
        "features": ["AST chunking", "Hybrid BM25+Vector", "Cross-Encoder rerank", "Call Graph", "Bounded agentic loop"],
        "repos_indexed": len(REPOS),
    }
