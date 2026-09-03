"""
llm_client.py — swappable LLM backends behind one interface.

The agent loop (agent.py) only ever calls `client.next_step(messages, tools)`
and gets back a normalized `LLMResponse`. That means the orchestration logic
is identical whether it's driven by the real Anthropic API or by the offline
MockLLMClient below — swap the class in main.py and nothing else changes.

MockLLMClient exists purely so this demo runs end-to-end with zero API keys
and zero network access. It's a small rule-based planner: it inspects the
user's question and the tool results seen so far, and decides which tool (if
any) to call next. It is NOT a substitute for a real model's reasoning — it's
a stand-in that exercises exactly the same tool-calling protocol a real LLM
would use, so the rest of the code (agent loop, tool dispatch, transcript
handling) is a real, working implementation, not a mock.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str | None                  # final natural-language answer, if any
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"     # "end_turn" | "tool_use"


# ---------------------------------------------------------------------------
# Real backend: Anthropic Messages API with native tool use.
# ---------------------------------------------------------------------------
class AnthropicClient:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic  # imported lazily so the mock path has no hard dep

        self._client = anthropic.Anthropic()
        self.model = model

    def next_step(self, messages: list[dict], tools: list[dict], system: str) -> LLMResponse:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=messages,
            tools=tools,
        )
        text_parts = [b.text for b in resp.content if b.type == "text"]
        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in resp.content
            if b.type == "tool_use"
        ]
        return LLMResponse(
            text="\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls,
            stop_reason=resp.stop_reason,
        )


# ---------------------------------------------------------------------------
# Offline mock backend: heuristic planner, same interface as above.
# ---------------------------------------------------------------------------
class MockLLMClient:
    """A minimal rule-based stand-in for an LLM, used when no API key is
    configured. It looks at the question + tool results gathered so far and
    decides the next tool call, then produces a final synthesis once it has
    enough evidence. Good enough to demonstrate the full agent loop offline.
    """

    def __init__(self):
        self._call_counter = 0

    def _next_id(self) -> str:
        self._call_counter += 1
        return f"mock_call_{self._call_counter}"

    def next_step(self, messages: list[dict], tools: list[dict], system: str) -> LLMResponse:
        user_question = messages[0]["content"]
        # Collect which tools have already been used, and their results, by
        # scanning the transcript we've built up so far.
        used_tools = set()
        tool_results = []
        for m in messages:
            if m["role"] == "assistant" and isinstance(m["content"], list):
                for block in m["content"]:
                    if block.get("type") == "tool_use":
                        used_tools.add(block["name"])
            if m["role"] == "user" and isinstance(m["content"], list):
                for block in m["content"]:
                    if block.get("type") == "tool_result":
                        tool_results.append(block["content"])

        q = user_question.lower()
        needs_math = bool(re.search(r"percent|%|growth|difference|ratio|how much (more|less)|total|sum|calculate", q))
        needs_internal = bool(re.search(r"internal|our (analyst|team|note)|confidential|risk model", q))
        needs_db = bool(re.search(r"sales|revenue|units|database|quarter|region", q))
        needs_web = bool(re.search(r"market|industry|news|report|global|public", q)) or not (needs_internal or needs_db)

        # Simple plan: internal docs -> database -> web -> calculator -> answer.
        if needs_internal and "document_retrieval" not in used_tools:
            return LLMResponse(
                text=None,
                tool_calls=[ToolCall(self._next_id(), "document_retrieval", {"query": user_question, "top_k": 2})],
                stop_reason="tool_use",
            )
        if needs_db and "database_query" not in used_tools:
            # crude heuristic query — a real model would write real SQL from schema + question
            return LLMResponse(
                text=None,
                tool_calls=[ToolCall(
                    self._next_id(), "database_query",
                    {"sql": "SELECT region, quarter, units, revenue_usd FROM sales ORDER BY quarter, region"},
                )],
                stop_reason="tool_use",
            )
        if needs_web and "web_search" not in used_tools:
            return LLMResponse(
                text=None,
                tool_calls=[ToolCall(self._next_id(), "web_search", {"query": user_question, "num_results": 3})],
                stop_reason="tool_use",
            )
        if needs_math and "calculator" not in used_tools and tool_results:
            # look for two numbers in the gathered evidence to demonstrate a calc step
            nums = re.findall(r"\d[\d,]*\.?\d*", " ".join(tool_results))
            nums = [n.replace(",", "") for n in nums][:2]
            expr = f"{nums[0]} - {nums[1]}" if len(nums) >= 2 else "0"
            return LLMResponse(
                text=None,
                tool_calls=[ToolCall(self._next_id(), "calculator", {"expression": expr})],
                stop_reason="tool_use",
            )

        # Enough evidence gathered (or nothing more to call) — synthesize a final answer.
        evidence = "\n---\n".join(tool_results) if tool_results else "(no tool evidence gathered)"
        answer = (
            "Based on the gathered evidence:\n\n"
            f"{evidence}\n\n"
            "[MOCK MODE: this synthesis is templated, not written by a real model. "
            "Set ANTHROPIC_API_KEY and use AnthropicClient for real reasoning over "
            "this same evidence.]"
        )
        return LLMResponse(text=answer, tool_calls=[], stop_reason="end_turn")


def get_default_client():
    """Pick a real client if an API key is present, else fall back to the mock."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicClient()
        except Exception:
            pass
    return MockLLMClient()
