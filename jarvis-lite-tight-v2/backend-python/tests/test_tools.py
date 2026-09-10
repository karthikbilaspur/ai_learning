"""Tests for app.tools that don't require network or a running gateway."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools import execute_tool, tell_joke, get_time, remember_note, JOKES


def test_get_time_returns_nonempty_string():
    assert isinstance(get_time({}), str)
    assert len(get_time({})) > 0


def test_tell_joke_returns_known_joke():
    assert tell_joke({}) in JOKES


def test_remember_note_requires_text():
    assert "Tell me what" in remember_note({})


def test_remember_note_accepts_text_key():
    result = remember_note({"text": "buy milk"})
    assert "buy milk" in result


def test_execute_tool_unknown_name():
    assert "Unknown tool" in execute_tool("does_not_exist", {})


def test_execute_tool_dispatches_correctly():
    assert execute_tool("tell_joke", {}) in JOKES
