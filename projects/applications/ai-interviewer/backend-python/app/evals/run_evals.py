"""
Runs the evaluator node against a fixed eval set and checks whether its
`better_answer` output covers the expected keywords for each question.
This is a real (if simple) precision proxy — not RAGAS, and this module
doesn't claim to be. It's useful as a regression check when you change the
prompt, the model, or the fallback heuristic.

Usage: python -m app.evals.run_evals
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.interviewer_graph import evaluator_node
from app.core.question_bank import QUESTION_BANK


def _find_question(question_text_prefix):
    """Returns (role, level, question_dict) so the evaluator is called with
    the same role/level bank the question actually belongs to — evaluating
    against the wrong bank silently falls back to bank[0], which previously
    made every eval case except the first look like a false failure."""
    for role, role_bank in QUESTION_BANK.items():
        for level, level_bank in role_bank.items():
            for q in level_bank:
                if q["question_text"].startswith(question_text_prefix):
                    return role, level, q
    return None, None, None


def run():
    eval_path = os.path.join(os.path.dirname(__file__), "eval_set.json")
    with open(eval_path) as f:
        eval_set = json.load(f)

    total = len(eval_set)
    passed = 0

    for case in eval_set:
        role, level, q = _find_question(case["question"])
        if not q:
            print(f"SKIP (question not found in bank): {case['question']}")
            continue

        # Simulate a reasonable candidate answer using the ideal answer
        # itself, to check the evaluator recognizes a correct answer as such.
        state = {
            "role": role,
            "level": level,
            "question_id": q["id"],
            "transcript": q["ideal_answer"],
        }
        result = evaluator_node(state)
        better_answer = result["evaluation"].get("better_answer", "").lower()

        keywords = [k.lower() for k in case["expected_keywords"]]
        hits = [k for k in keywords if k in better_answer]
        ok = len(hits) >= max(1, len(keywords) // 2)
        passed += int(ok)

        print(f"{'PASS' if ok else 'FAIL'}: {case['question']}  "
              f"({len(hits)}/{len(keywords)} keywords, score={result['evaluation'].get('score')}, "
              f"llm_scored={result['evaluation'].get('llm_scored')})")

    print(f"\n{passed}/{total} eval cases passed keyword coverage check.")


if __name__ == "__main__":
    run()
