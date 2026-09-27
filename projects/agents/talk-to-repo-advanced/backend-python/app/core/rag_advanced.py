"""
Hybrid retrieval (vector + BM25) with cross-encoder reranking, plus a
bounded agentic loop: the model can ask to read one more full file before
giving its final answer, up to MAX_AGENT_STEPS extra passes.

This used to have a "NEED_MORE" instruction in the prompt that nothing
ever acted on. It now actually parses that marker, fetches the file
through the same path-safety check used by /read-file, and re-prompts
with the extra context — so it's genuinely iterative, just bounded so a
confused model can't loop forever.
"""

import json
import os
import re

import requests

from .ingester import load_call_graph
from .paths import safe_repo_path
from ..vectorstore import get_chroma, get_cross_encoder, get_embedding_model
from rank_bm25 import BM25Okapi

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:13b")

MAX_AGENT_STEPS = 2  # extra file-read passes beyond the first answer
MAX_EXTRA_FILE_CHARS = 4000
NEED_MORE_RE = re.compile(r"NEED_MORE:\s*([^\s`]+)")

DATA_ROOT = "./chroma_db"


def hybrid_search(repo_id: str, query: str, top_k: int = 20):
    chroma = get_chroma(repo_id)
    embed_model = get_embedding_model()
    q_emb = embed_model.encode([query]).tolist()

    vec_res = chroma.query(query_embeddings=q_emb, n_results=top_k)
    vec_docs = vec_res["documents"][0]
    vec_metas = vec_res["metadatas"][0]

    bm25_docs, bm25_metas = [], []
    try:
        with open(os.path.join(DATA_ROOT, repo_id, "bm25.json")) as f:
            chunks = json.load(f)["chunks"]
        corpus = [c["text"] for c in chunks]
        bm25 = BM25Okapi([c.split() for c in corpus])
        scores = bm25.get_scores(query.split())
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        bm25_docs = [corpus[i] for i in top_idx]
        bm25_metas = [
            {"file": chunks[i]["file"], "line": chunks[i]["start_line"], "type": chunks[i]["type"], "name": chunks[i].get("name", "")}
            for i in top_idx
        ]
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BM25 unavailable for {repo_id}: {exc}")

    merged = {}
    for doc, meta in zip(vec_docs, vec_metas):
        merged[doc] = meta
    for doc, meta in zip(bm25_docs, bm25_metas):
        merged.setdefault(doc, meta)

    return list(merged.items())[:top_k]


def rerank(query: str, candidates: list):
    if not candidates:
        return []
    try:
        cross = get_cross_encoder()
        pairs = [[query, doc] for doc, _meta in candidates]
        scores = cross.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
        return [(doc, meta, float(score)) for (doc, meta), score in ranked]
    except Exception as exc:
        print(f"Rerank failed ({exc}), falling back to vector/BM25 order")
        return [(doc, meta, 0.8) for doc, meta in candidates[:5]]


def _build_citations(reranked: list):
    return [
        {"file": meta["file"], "line": meta["line"], "type": meta["type"], "name": meta.get("name", ""), "score": score, "content": doc[:500]}
        for doc, meta, score in reranked
    ]


def _relevant_call_graph(repo_id: str, citations: list, max_nodes: int = 40, max_edges: int = 60) -> dict:
    """
    A readable subgraph, not the whole repo: the functions/files that
    showed up in the answer's citations, plus their direct callers and
    callees (one hop), capped so the frontend graph stays legible.
    """
    graph = load_call_graph(repo_id)
    if not graph["nodes"]:
        return {"nodes": [], "edges": []}

    by_id = {n["id"]: n for n in graph["nodes"]}
    cite_names = {c["name"] for c in citations if c.get("name")}
    cite_files = {c["file"] for c in citations}

    seed_ids = {n["id"] for n in graph["nodes"] if n["label"] in cite_names or n["file"] in cite_files}
    included = set(seed_ids)
    for edge in graph["edges"]:
        if edge["source"] in seed_ids or edge["target"] in seed_ids:
            included.add(edge["source"])
            included.add(edge["target"])

    nodes = [by_id[i] for i in included if i in by_id][:max_nodes]
    node_ids = {n["id"] for n in nodes}
    edges = [e for e in graph["edges"] if e["source"] in node_ids and e["target"] in node_ids][:max_edges]
    return {"nodes": nodes, "edges": edges}


def _read_full_file(repo_id: str, relative_path: str) -> str | None:
    resolved = safe_repo_path(repo_id, relative_path)
    if resolved is None or not os.path.isfile(resolved):
        return None
    try:
        with open(resolved, errors="ignore") as f:
            return f.read()[:MAX_EXTRA_FILE_CHARS]
    except OSError:
        return None


def _build_prompt(question: str, context: str) -> str:
    return f"""You are an expert senior engineer. Answer the user's question using the code context below. Be precise, cite files like `src/auth.js:12`.

Context:
{context}

Question: {question}

If you genuinely need to see the full contents of one more specific file to answer well, end your response with exactly: NEED_MORE: <relative/file/path>
Otherwise just give your final answer.

Answer:
"""


def _stream_ollama(prompt: str):
    """Yields response tokens; raises on connection failure so the caller
    can emit a single clear error instead of a half-written answer."""
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
        stream=True,
        timeout=60,
    )
    resp.raise_for_status()
    for line in resp.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        yield data.get("response", "")
        if data.get("done"):
            break


def agentic_query_stream(repo_id: str, question: str):
    yield {"token": f"🔍 Hybrid search (vector + BM25) for: {question}\n"}
    candidates = hybrid_search(repo_id, question, top_k=20)
    yield {"token": f"Found {len(candidates)} candidates, reranking with cross-encoder...\n\n"}

    reranked = rerank(question, candidates)
    if not reranked:
        yield {"token": "No indexed content matched this question. Try ingesting the repo again or rephrasing.\n"}
        return

    citations = _build_citations(reranked)
    yield {"citations": citations}
    yield {"graph": _relevant_call_graph(repo_id, citations)}

    context = "\n\n".join(f"[{meta['file']}:{meta['line']} - {meta['type']}]\n{doc}" for doc, meta, _score in reranked)
    seen_files: set[str] = set()

    try:
        for step in range(MAX_AGENT_STEPS + 1):
            prompt = _build_prompt(question, context)
            step_answer = ""
            for token in _stream_ollama(prompt):
                step_answer += token
                yield {"token": token}

            match = NEED_MORE_RE.search(step_answer)
            if not match or step == MAX_AGENT_STEPS:
                break

            requested = match.group(1).strip().strip(".,")
            if requested in seen_files:
                break
            seen_files.add(requested)

            file_content = _read_full_file(repo_id, requested)
            if file_content is None:
                yield {"token": f"\n\n[Could not read {requested} — stopping here.]\n"}
                break

            yield {"token": f"\n\n---\n🔁 Reading {requested} for more context (step {step + 2})...\n---\n\n"}
            context += f"\n\n[FULL FILE: {requested}]\n{file_content}"
    except requests.RequestException as exc:
        yield {"token": f"\n\n[Ollama unavailable — start it and pull {OLLAMA_MODEL}. Error: {exc}]\n"}
