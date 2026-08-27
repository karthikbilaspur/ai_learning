"""
agent.py — the actual agent loop.

This is the "few hours" part of the project mentioned earlier: a single loop
that alternates between (1) asking the model what to do next and (2)
executing whatever tool it asked for, feeding the result back in, until the
model produces a final answer instead of another tool call.

Everything here is written against the LLMResponse/ToolCall interface in
llm_client.py, so it's backend-agnostic — same loop for a real Anthropic
client or the offline mock.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from llm_client import LLMResponse, ToolCall
from tools import TOOL_IMPLS, TOOL_SCHEMAS

SYSTEM_PROMPT = """You are a focused research agent. You have four tools:
- document_retrieval: search internal/private analyst documents
- database_query: run read-only SQL against the research database
- web_search: search the public web
- calculator: evaluate arithmetic expressions

Rules:
1. Only call a tool when you actually need information or computation you
   don't already have. Don't call a tool "just in case."
2. Never do arithmetic yourself — always use the calculator tool for any
   computation, however simple.
3. Prefer internal documents and the database over the public web when the
   question is about the company's own data.
4. When you have enough evidence, stop calling tools and write a final answer
   that cites which source (document / database / web) each claim came from.
5. If a tool returns an error, don't repeat the exact same call — either fix
   the input or work around it.
"""


@dataclass
class AgentStep:
    kind: str  # "tool_call" | "tool_result" | "final_answer"
    detail: str


@dataclass
class AgentTrace:
    steps: list[AgentStep] = field(default_factory=list)

    def log(self, kind: str, detail: str):
        self.steps.append(AgentStep(kind, detail))


class ResearchAgent:
    def __init__(self, llm_client, max_iterations: int = 6, verbose: bool = True):
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.verbose = verbose

    def run(self, question: str) -> tuple[str, AgentTrace]:
        trace = AgentTrace()
        messages: list[dict] = [{"role": "user", "content": question}]

        for iteration in range(1, self.max_iterations + 1):
            response: LLMResponse = self.llm_client.next_step(
                messages, TOOL_SCHEMAS, SYSTEM_PROMPT
            )

            if response.stop_reason != "tool_use" or not response.tool_calls:
                final = response.text or "(no answer produced)"
                trace.log("final_answer", final)
                return final, trace

            # Record the assistant's tool-call turn in the transcript so the
            # next call to the model has full context of what it already did.
            messages.append({
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input}
                    for tc in response.tool_calls
                ],
            })

            # Execute every requested tool call and append results.
            result_blocks = []
            for tc in response.tool_calls:
                trace.log("tool_call", f"{tc.name}({tc.input})")
                result_text = self._execute_tool(tc)
                trace.log("tool_result", result_text[:500])
                result_blocks.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result_text,
                })
            messages.append({"role": "user", "content": result_blocks})

        # Ran out of iterations without a final answer — fail loudly rather
        # than silently returning nothing.
        trace.log("final_answer", "(stopped: hit max_iterations without a final answer)")
        return "I wasn't able to reach a final answer within the iteration budget.", trace

    def _execute_tool(self, tc: ToolCall) -> str:
        impl = TOOL_IMPLS.get(tc.name)
        if impl is None:
            return f"ERROR: unknown tool '{tc.name}'"
        try:
            return impl(**tc.input)
        except TypeError as e:
            return f"ERROR: bad arguments for '{tc.name}': {e}"
        except Exception as e:
            return f"ERROR: '{tc.name}' failed: {e}"
