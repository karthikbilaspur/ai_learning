"""Local + remote tools the LLM can invoke."""
import datetime
import json
import os
import random
import requests

NOTES_FILE = os.getenv("NOTES_FILE", "./data/notes.json")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:5000")

os.makedirs(os.path.dirname(NOTES_FILE) or ".", exist_ok=True)

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I asked my AI for a joke. It said: 404 humor not found.",
    "I have a joke about recursion, but first I have to tell you a joke about recursion.",
]


def get_time(_args: dict) -> str:
    return datetime.datetime.now().astimezone().strftime("%I:%M %p, %A %B %d")


def get_weather(args: dict) -> str:
    city = args.get("city", "Bangalore")
    try:
        resp = requests.get(f"https://wttr.in/{city}", params={"format": "%C+%t"}, timeout=3)
        if resp.ok:
            return resp.text.strip()
    except requests.RequestException as exc:
        print(f"[tools] weather lookup failed: {exc}")
    return f"Weather is unavailable right now for {city}."


def tell_joke(_args: dict) -> str:
    return random.choice(JOKES)


def remember_note(args: dict) -> str:
    note = (args.get("text") or args.get("note") or "").strip()
    if not note:
        return "Tell me what you want me to remember."
    try:
        data = json.load(open(NOTES_FILE)) if os.path.exists(NOTES_FILE) else []
    except (json.JSONDecodeError, OSError):
        data = []
    data.append({"note": note, "time": datetime.datetime.now().astimezone().isoformat()})
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return f"Noted: {note}"


def list_events_today(_args: dict) -> str:
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/calendar/events/today", timeout=5)
    except requests.RequestException as exc:
        return f"I could not reach the calendar gateway ({exc})."
    if resp.status_code == 401:
        return "Google Calendar is not connected yet."
    if not resp.ok:
        return "I could not read the calendar."
    events = resp.json()
    if not events:
        return "Your calendar is clear today."
    summary = ", ".join(f"{e['summary']} at {e['start']}" for e in events[:8])
    return f"Today: {summary}"


def create_event(args: dict) -> str:
    title = args.get("title") or args.get("summary")
    start, end = args.get("start"), args.get("end")
    if not title or not start or not end:
        return "To create an event I need a title, start time, and end time."
    payload = {
        "title": title,
        "start": start,
        "end": end,
        "description": args.get("description", ""),
        "location": args.get("location", ""),
    }
    try:
        resp = requests.post(f"{GATEWAY_URL}/api/calendar/events", json=payload, timeout=10)
    except requests.RequestException as exc:
        return f"I could not reach the calendar gateway ({exc})."
    if resp.status_code == 401:
        return "Google Calendar is not connected yet."
    if not resp.ok:
        return "Calendar rejected the event."
    return f"Created '{title}' on your calendar."


AVAILABLE_TOOLS = {
    "get_time": get_time,
    "get_weather": get_weather,
    "tell_joke": tell_joke,
    "remember_note": remember_note,
    "list_events_today": list_events_today,
    "create_event": create_event,
}


def execute_tool(name: str, args: dict) -> str:
    handler = AVAILABLE_TOOLS.get(name)
    if handler is None:
        return f"Unknown tool: {name}"
    return handler(args or {})
