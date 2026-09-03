"""
tools.py — the 3-4 tools the research agent can call.

Each tool has:
  1. a JSON schema (so an LLM's native tool-calling / function-calling API knows
     how to call it), and
  2. a plain Python function that actually executes it and returns a string
     result (tool results going back to an LLM should always be strings).

Design notes:
  - Every tool is defensive: bad input returns a readable error string instead
    of raising, so the agent loop can hand the error back to the model and let
    it retry/recover instead of crashing the whole run.
  - Tools are intentionally "dumb" and single-purpose. Orchestration (deciding
    which tool to call, how many times, in what order) is the agent's job, not
    the tool's.
"""

from __future__ import annotations

import ast
import operator
import os
import re
import sqlite3
from dataclasses import dataclass
from typing import Callable

# ---------------------------------------------------------------------------
# 1. CALCULATOR
# ---------------------------------------------------------------------------
# Safe arithmetic evaluation using the `ast` module instead of eval(). We only
# allow a whitelist of node types / operators, so `__import__('os').system(...)`
# style injection attacks are structurally impossible, not just filtered out.

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Disallowed expression element: {type(node).__name__}")


def calculator(expression: str) -> str:
    """Evaluate a pure arithmetic expression, e.g. '(1350 * 12) / 4 - 7**2'."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"ERROR: could not evaluate '{expression}': {e}"


# ---------------------------------------------------------------------------
# 2. WEB SEARCH
# ---------------------------------------------------------------------------
# Real implementation hits a search API (Tavily/Serper/Bing) if a key is
# configured. Falls back to a tiny local "web index" so this demo runs fully
# offline / without any API keys. Swap _offline_search for a real HTTP call
# and nothing else in the agent needs to change — that's the point of giving
# tools a stable string-in/string-out interface.

_MOCK_WEB_INDEX = [
    {
        "title": "Global EV Sales Report 2025",
        "url": "https://example-research.org/ev-sales-2025",
        "snippet": (
            "Global electric vehicle sales reached 17.1 million units in 2025, "
            "a 22% increase over 2024. China accounted for roughly 60% of sales, "
            "followed by Europe at 21% and the United States at 12%."
        ),
    },
    {
        "title": "Battery Prices Continue to Fall",
        "url": "https://example-research.org/battery-prices",
        "snippet": (
            "Lithium-ion battery pack prices fell to $89/kWh in 2025, down from "
            "$139/kWh in 2022. Analysts expect prices to approach $70/kWh by 2027 "
            "as LFP chemistry adoption grows."
        ),
    },
    {
        "title": "US EV Tax Credit Rules Explained",
        "url": "https://example-research.org/us-ev-tax-credit",
        "snippet": (
            "The US federal EV tax credit offers up to $7,500 for qualifying new "
            "vehicles, subject to income caps, price caps, and battery sourcing "
            "requirements under the Inflation Reduction Act."
        ),
    },
    {
        "title": "Charging Infrastructure Growth",
        "url": "https://example-research.org/charging-infra",
        "snippet": (
            "Public charging ports in the US grew to 210,000 in 2025, up from "
            "160,000 in 2023. Fast-charging (DC) ports remain a minority of "
            "total ports but are growing faster than Level 2 ports."
        ),
    },
]


def _offline_search(query: str, k: int) -> list[dict]:
    q_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored = []
    for doc in _MOCK_WEB_INDEX:
        text = (doc["title"] + " " + doc["snippet"]).lower()
        d_terms = set(re.findall(r"[a-z0-9]+", text))
        overlap = len(q_terms & d_terms)
        if overlap:
            scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:k]] or _MOCK_WEB_INDEX[:k]


def web_search(query: str, num_results: int = 3) -> str:
    """Search the web for `query`, return top results as title/url/snippet."""
    api_key = os.environ.get("SEARCH_API_KEY")
    if api_key:
        # --- real implementation would go here, e.g. Tavily ---
        # import requests
        # resp = requests.post("https://api.tavily.com/search",
        #                       json={"api_key": api_key, "query": query,
        #                             "max_results": num_results}, timeout=10)
        # results = resp.json()["results"]
        pass  # fall through to offline mode if the real call isn't wired up

    results = _offline_search(query, num_results)
    if not results:
        return f"No results found for '{query}'."
    lines = [f"[OFFLINE-DEMO MODE — no SEARCH_API_KEY set] Results for '{query}':"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']} ({r['url']})\n   {r['snippet']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. DOCUMENT RETRIEVAL (local corpus, TF-IDF cosine similarity)
# ---------------------------------------------------------------------------
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_DOC_DIR = os.path.join(os.path.dirname(__file__), "data", "docs")


@dataclass
class _Corpus:
    ids: list[str]
    texts: list[str]
    vectorizer: TfidfVectorizer
    matrix: any


_corpus: _Corpus | None = None


def _load_corpus() -> _Corpus:
    global _corpus
    if _corpus is not None:
        return _corpus
    ids, texts = [], []
    for fname in sorted(os.listdir(_DOC_DIR)):
        if fname.endswith(".txt"):
            with open(os.path.join(_DOC_DIR, fname), encoding="utf-8") as f:
                texts.append(f.read())
                ids.append(fname)
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    _corpus = _Corpus(ids=ids, texts=texts, vectorizer=vectorizer, matrix=matrix)
    return _corpus


def document_retrieval(query: str, top_k: int = 2) -> str:
    """Retrieve the most relevant chunks from the local internal document corpus."""
    corpus = _load_corpus()
    if not corpus.ids:
        return "ERROR: no documents indexed in data/docs/."
    q_vec = corpus.vectorizer.transform([query])
    sims = cosine_similarity(q_vec, corpus.matrix)[0]
    ranked = sorted(zip(corpus.ids, corpus.texts, sims), key=lambda x: x[2], reverse=True)
    top = [r for r in ranked if r[2] > 0][:top_k]
    if not top:
        return f"No relevant internal documents found for '{query}'."
    lines = [f"Top {len(top)} internal document matches for '{query}':"]
    for doc_id, text, score in top:
        snippet = text.strip().replace("\n", " ")
        snippet = snippet[:400] + ("..." if len(snippet) > 400 else "")
        lines.append(f"- {doc_id} (relevance {score:.2f}): {snippet}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. DATABASE QUERY (SQLite, read-only guardrail)
# ---------------------------------------------------------------------------

_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "research.db")

_FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace)\b", re.IGNORECASE
)


def database_query(sql: str) -> str:
    """Run a read-only SQL SELECT against the local research database."""
    if not sql.strip().lower().startswith("select"):
        return "ERROR: only SELECT statements are permitted."
    if _FORBIDDEN_SQL.search(sql):
        return "ERROR: query contains a disallowed keyword (writes/schema changes are blocked)."
    try:
        conn = sqlite3.connect(f"file:{_DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = cur.fetchmany(50)  # cap result size fed back to the model
        conn.close()
        if not rows:
            return "Query returned no rows."
        cols = rows[0].keys()
        lines = [", ".join(cols)]
        for row in rows:
            lines.append(", ".join(str(row[c]) for c in cols))
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR: query failed: {e}"


# ---------------------------------------------------------------------------
# Tool registry: schema + callable, in one place. This is what gets handed to
# the LLM client (as tool schemas) and to the agent loop (as a dispatch table).
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression. Use for any math: sums, "
        "percentages, growth rates, unit conversions, etc. Do not do math in your head.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python-style arithmetic expression, e.g. '17100000 * 0.22'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the public web for current information, news, or facts "
        "not contained in the internal document corpus or database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {
                    "type": "integer",
                    "description": "How many results to return (default 3)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "document_retrieval",
        "description": "Search the internal/private document corpus (analyst notes, "
        "internal reports) for relevant passages. Use this before web_search when the "
        "question might be answered by internal research documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look for"},
                "top_k": {"type": "integer", "description": "Number of chunks to return (default 2)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "database_query",
        "description": "Run a read-only SQL SELECT query against the research database. "
        "Tables: sales(id, region, quarter, units, revenue_usd), "
        "products(id, name, category, launch_year). Use this for structured/numeric "
        "questions about sales, regions, or products.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "A SELECT statement"}
            },
            "required": ["sql"],
        },
    },
]

TOOL_IMPLS: dict[str, Callable[..., str]] = {
    "calculator": calculator,
    "web_search": web_search,
    "document_retrieval": document_retrieval,
    "database_query": database_query,
}
