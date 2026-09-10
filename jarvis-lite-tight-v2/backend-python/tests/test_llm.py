"""Tests for the tool-call parsing logic in app.llm.

Run with: pytest backend-python/tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.llm import parse_tool_call


def test_parses_clean_json_tool_call():
    text = '{"tool": "get_weather", "arguments": {"city": "Bangalore"}}'
    result = parse_tool_call(text)
    assert result == {"tool": "get_weather", "arguments": {"city": "Bangalore"}}


def test_parses_tool_call_embedded_in_prose():
    text = 'Sure thing! {"tool": "tell_joke", "arguments": {}} Hope that helps.'
    result = parse_tool_call(text)
    assert result["tool"] == "tell_joke"


def test_ignores_unknown_tool_names():
    text = '{"tool": "delete_all_files", "arguments": {}}'
    assert parse_tool_call(text) is None


def test_returns_none_for_plain_text():
    text = "The weather in Bangalore is sunny today."
    assert parse_tool_call(text) is None


def test_returns_none_for_empty_input():
    assert parse_tool_call("") is None
    assert parse_tool_call(None) is None


def test_ignores_malformed_json_and_falls_through():
    text = '{not valid json} but here is one: {"tool": "get_time", "arguments": {}}'
    result = parse_tool_call(text)
    assert result is not None
    assert result["tool"] == "get_time"


def test_handles_multiple_brace_groups_without_merging_them():
    # A naive greedy `{.*}` regex spans from the FIRST '{' to the LAST '}',
    # which would swallow both fragments below into one invalid blob.
    text = 'Note: {this is just a stray brace} Calling {"tool": "tell_joke", "arguments": {}} now.'
    result = parse_tool_call(text)
    assert result is not None
    assert result["tool"] == "tell_joke"
