"""LLM orchestration: fast-path answers, Ollama calls, and tool-call parsing."""
import datetime
import json
import os

import requests

from .tools import execute_tool, AVAILABLE_TOOLS

SYSTEM_PROMPT = """You are JARVIS, a concise local voice assistant.
Return either normal text or exactly one JSON object of the shape:
{{"tool": "tool_name", "arguments": {{...}}}}

Available tools:
- get_time
- get_weather(city)
- tell_joke
- remember_note(text)
- list_events_today
- create_event(title, start, end, description?, location?)

Use create_event only when all required fields are known. Never invent calendar details.
Current local time: {time}
"""

TIME_KEYWORDS = ("what time", "current time", "time is it", "clock")
JOKE_PHRASES = ("tell me a joke", "tell a joke", "joke")


def _extract_json_objects(text: str) -> list[str]:
    """Find candidate top-level {...} substrings using brace matching.

    A naive `\\{.*\\}` regex greedily spans from the *first* '{' to the
    *last* '}' in the text, which breaks as soon as a response contains more
    than one brace-delimited chunk (e.g. stray braces in prose, or two tool
    calls). Scanning brace depth avoids that failure mode.
    """
    objects = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    objects.append(text[start : i + 1])
                    start = None
    return objects


def call_ollama(prompt: str) -> str | None:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    try:
        resp = requests.post(url, json={"model": model, "prompt": prompt, "stream": False}, timeout=45)
        if resp.ok:
            return resp.json().get("response", "").strip()
    except requests.RequestException as exc:
        print(f"[llm] Ollama unavailable: {exc}")
    return None


def parse_tool_call(text: str) -> dict | None:
    """Extract the first valid `{"tool": ..., "arguments": {...}}` object from text."""
    if not text:
        return None
    for candidate in _extract_json_objects(text):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("tool") in AVAILABLE_TOOLS:
            return obj
    return None


def _fast_path(transcript: str) -> tuple[str, str] | None:
    """Cheap, deterministic answers that don't need the LLM at all."""
    lower = transcript.lower().strip()
    if any(word in lower for word in TIME_KEYWORDS):
        now = datetime.datetime.now().astimezone().strftime("%I:%M %p")
        return f"It is {now}.", "get_time"
    if lower in JOKE_PHRASES:
        return execute_tool("tell_joke", {}), "tell_joke"
    return None


def get_ai_response(transcript: str, history: list) -> tuple[str, str | None]:
    """Return (reply_text, tool_name_or_None) for a user transcript."""
    fast = _fast_path(transcript)
    if fast:
        return fast

    prompt = (
        SYSTEM_PROMPT.format(time=datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"))
        + f"\nRecent history: {json.dumps(history[-5:])}\nUser: {transcript}\nJARVIS:"
    )
    raw = call_ollama(prompt)

    tool_call = parse_tool_call(raw)
    if tool_call:
        tool_name = tool_call["tool"]
        return execute_tool(tool_name, tool_call.get("arguments", {})), tool_name

    if raw:
        return raw, None

    return "My local language model is unavailable. Start Ollama and try again.", None
