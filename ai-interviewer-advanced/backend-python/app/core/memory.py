"""
Per-session memory backed by SQLite (instead of one shared /tmp JSON file
that collided across every user/tab). Tracks strengths/weaknesses by
category, session count, and simple entity facts extracted from answers.

Entity extraction here is intentionally simple keyword matching, not an
NLP claim we can't back up: it just flags technologies the candidate
mentioned, which is genuinely useful for follow-up question selection.
"""
import sqlite3
import os
import re
import json
import threading

DB_PATH = os.getenv("INTERVIEWER_DB", "/tmp/interviewer_memory.db")
_lock = threading.Lock()

_KNOWN_ENTITIES = [
    "React", "Vue", "Angular", "Node.js", "Node", "Python", "Django", "FastAPI",
    "Postgres", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kubernetes", "Docker",
    "GraphQL", "REST", "Kafka", "RabbitMQ", "TypeScript", "JavaScript", "AWS",
    "Chroma", "ChromaDB", "pgvector", "Langfuse", "BM25", "Webpack", "Vite",
]


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            sessions_count INTEGER DEFAULT 0
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS category_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            category TEXT,
            score INTEGER
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS entity_facts (
            session_id TEXT,
            fact TEXT,
            UNIQUE(session_id, fact)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS asked_questions (
            session_id TEXT,
            question_id TEXT,
            UNIQUE(session_id, question_id)
        )"""
    )
    return c


def _extract_entities(transcript: str):
    found = []
    lower = transcript.lower()
    for ent in _KNOWN_ENTITIES:
        if ent.lower() in lower and f"Knows {ent}" not in found:
            found.append(f"Knows {ent}")
    return found


def get_memory(session_id: str):
    with _lock, _conn() as c:
        row = c.execute(
            "SELECT sessions_count FROM sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        sessions_count = row[0] if row else 0

        scores = c.execute(
            "SELECT category, score FROM category_scores WHERE session_id=?",
            (session_id,),
        ).fetchall()
        by_cat = {}
        for category, score in scores:
            by_cat.setdefault(category, []).append(score)

        strengths = sorted({cat for cat, s in by_cat.items() if sum(s) / len(s) >= 7})
        weaknesses = sorted({cat for cat, s in by_cat.items() if sum(s) / len(s) < 7})

        facts = [r[0] for r in c.execute(
            "SELECT fact FROM entity_facts WHERE session_id=?", (session_id,)
        ).fetchall()]

        asked = [r[0] for r in c.execute(
            "SELECT question_id FROM asked_questions WHERE session_id=?", (session_id,)
        ).fetchall()]

        return {
            "session_id": session_id,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "sessions": sessions_count,
            "entity_facts": facts,
            "asked_question_ids": asked,
            "category_history": by_cat,
        }


def record_question_asked(session_id: str, question_id: str):
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO asked_questions (session_id, question_id) VALUES (?, ?)",
            (session_id, question_id),
        )
        c.execute(
            "INSERT INTO sessions (session_id, sessions_count) VALUES (?, 1) "
            "ON CONFLICT(session_id) DO UPDATE SET sessions_count = sessions_count",
            (session_id,),
        )


def update_memory(session_id: str, transcript: str, evaluation: dict, category: str):
    with _lock, _conn() as c:
        score = evaluation.get("score", 5)
        c.execute(
            "INSERT INTO category_scores (session_id, category, score) VALUES (?, ?, ?)",
            (session_id, category, score),
        )
        for fact in _extract_entities(transcript):
            c.execute(
                "INSERT OR IGNORE INTO entity_facts (session_id, fact) VALUES (?, ?)",
                (session_id, fact),
            )
        c.execute(
            "INSERT INTO sessions (session_id, sessions_count) VALUES (?, 1) "
            "ON CONFLICT(session_id) DO UPDATE SET sessions_count = sessions_count + 1",
            (session_id,),
        )
    return get_memory(session_id)
