import sys

from agent import ResearchAgent
from llm_client import get_default_client


def print_trace(trace):
    print("\n--- agent trace ---")
    for step in trace.steps:
        if step.kind == "tool_call":
            print(f"  [tool call]   {step.detail}")
        elif step.kind == "tool_result":
            print(f"  [tool result] {step.detail}")
        elif step.kind == "final_answer":
            print(f"  [final]       (see answer below)")
    print("--- end trace ---\n")


def main():
    question = " ".join(sys.argv[1:]) or (
        "How did APAC sales compare to Europe sales in Q2 2025, and is there "
        "any internal analyst commentary on APAC market risk?"
    )
    client = get_default_client()
    print(f"Using LLM backend: {type(client).__name__}")
    print(f"Question: {question}\n")

    agent = ResearchAgent(client)
    answer, trace = agent.run(question)

    print_trace(trace)
    print("ANSWER:\n" + answer)


if __name__ == "__main__":
    main()
