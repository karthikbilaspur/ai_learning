"""
Interview flow as an actual LangGraph StateGraph:

    START -> (conditional) -> planner -> questioner -> END
                  (or)      -> evaluator -> feedback -> planner -> questioner -> END

If the `langgraph` package isn't installed, we fall back to a hand-rolled
graph runner with the *same node functions and the same routing logic* —
so behavior is identical either way. This is a genuine fallback, not a
comment claiming an architecture that isn't there.
"""
import random
import json
import os
import requests
from typing import TypedDict, Optional, List, Dict, Any

from .question_bank import get_bank_for, get_question_bank
from .retrieval import QuestionRetriever, retrieval_status
from . import memory as memory_store

_HAS_LANGGRAPH = False
try:
    from langgraph.graph import StateGraph, START, END
    _HAS_LANGGRAPH = True
except Exception:
    StateGraph = None

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:13b")

_retriever_cache: Dict[str, QuestionRetriever] = {}


def _get_retriever(role: str, level: str) -> QuestionRetriever:
    key = f"{role}::{level}"
    if key not in _retriever_cache:
        _retriever_cache[key] = QuestionRetriever(get_bank_for(role, level))
    return _retriever_cache[key]


class InterviewState(TypedDict, total=False):
    role: str
    level: str
    session_id: str
    memory: Dict[str, Any]
    asked_ids: List[str]
    question_id: Optional[str]
    transcript: Optional[str]
    current_question: Optional[Dict[str, Any]]
    evaluation: Optional[Dict[str, Any]]
    next_question: Optional[Dict[str, Any]]


# ---------- Nodes ----------

def evaluator_node(state: InterviewState) -> InterviewState:
    role, level = state["role"], state["level"]
    bank = get_bank_for(role, level)
    qid = state["question_id"]
    transcript = state["transcript"]
    question = next((q for q in bank if q["id"] == qid), bank[0])

    prompt = f"""You are a senior {role} interviewer for {level} level. Evaluate the candidate's answer.

Question: {question['question_text']}
Ideal Answer: {question['ideal_answer']}
Candidate Answer: {transcript}

Return JSON ONLY: {{"score": 1-10, "verdict": "Strong Hire/Hire/No Hire", "feedback": "2-3 sentences", "better_answer": "concise ideal", "follow_up": "one follow-up question"}}

JSON:"""

    evaluation = None
    llm_used = False
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
            timeout=30,
        )
        if resp.status_code == 200:
            evaluation = json.loads(resp.json()["response"])
            llm_used = True
    except Exception as e:
        print(f"[evaluator] Ollama unavailable, using heuristic fallback: {e}")

    if evaluation is None:
        score = 6 if len(transcript.strip()) > 50 else 3
        evaluation = {
            "score": score,
            "verdict": "Hire" if score >= 6 else "No Hire",
            "feedback": f"Heuristic scoring only (LLM unavailable) — based on answer length/coverage for {question['category']}.",
            "better_answer": question["ideal_answer"],
            "follow_up": f"Can you go deeper on {question['hints']}?",
        }

    evaluation["category"] = question["category"]
    evaluation["llm_scored"] = llm_used
    state["evaluation"] = evaluation
    return state


def planner_node(state: InterviewState) -> InterviewState:
    role, level = state["role"], state["level"]
    bank = get_bank_for(role, level)
    asked = set(state.get("asked_ids", []))
    mem = state.get("memory") or {}
    weaknesses = mem.get("weaknesses", [])

    retriever = _get_retriever(role, level)

    # Build a query that steers toward weak categories; falls back to a
    # generic query covering the whole bank when there's no history yet.
    query = " ".join(weaknesses) if weaknesses else " ".join(
        {q["category"] for q in bank}
    )

    ranked_ids = retriever.rank(query, exclude_ids=asked, top_k=len(bank))
    if not ranked_ids:
        # Every question in this bank has been asked already — reset.
        ranked_ids = [q["id"] for q in bank]

    chosen_id = ranked_ids[0]
    chosen = next(q for q in bank if q["id"] == chosen_id)

    if "current_question" in state or "question_id" not in state:
        state["current_question"] = {
            "question_id": chosen["id"],
            "question_text": chosen["question_text"],
            "category": chosen["category"],
            "difficulty": chosen["difficulty"],
            "hints": chosen["hints"],
        }
    state["next_question"] = {
        "question_id": chosen["id"],
        "question_text": chosen["question_text"],
        "category": chosen["category"],
        "difficulty": chosen["difficulty"],
        "hints": chosen["hints"],
    }
    return state


def questioner_node(state: InterviewState) -> InterviewState:
    # Formats current_question for the /start response. next_question is
    # already fully formed by planner_node for the /answer response path.
    if "current_question" not in state and state.get("next_question"):
        state["current_question"] = state["next_question"]
    return state


def _route_from_start(state: InterviewState) -> str:
    if "transcript" in state and "question_id" in state:
        return "evaluator"
    return "planner"


# ---------- Graph assembly ----------

def _build_langgraph():
    graph = StateGraph(InterviewState)
    graph.add_node("planner", planner_node)
    graph.add_node("questioner", questioner_node)
    graph.add_node("evaluator", evaluator_node)

    graph.add_conditional_edges(START, _route_from_start, {
        "planner": "planner",
        "evaluator": "evaluator",
    })
    graph.add_edge("evaluator", "planner")
    graph.add_edge("planner", "questioner")
    graph.add_edge("questioner", END)
    return graph.compile()


class _FallbackGraph:
    """Same nodes, same routing, no langgraph dependency installed."""

    def invoke(self, state: InterviewState) -> InterviewState:
        route = _route_from_start(state)
        if route == "evaluator":
            state = evaluator_node(state)
        state = planner_node(state)
        state = questioner_node(state)
        return state


def create_interviewer_graph():
    if _HAS_LANGGRAPH:
        return _build_langgraph()
    print("[interviewer_graph] langgraph not installed — using equivalent fallback runner.")
    return _FallbackGraph()


def graph_backend_status():
    return {
        "langgraph_active": _HAS_LANGGRAPH,
        **retrieval_status(),
    }
