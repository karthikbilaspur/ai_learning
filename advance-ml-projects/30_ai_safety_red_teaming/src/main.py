"""End-to-end red-team run: generate attacks against a target, score
Attack Success Rate, then check how much a guardrail would have blocked
(previously there was no script tying red_team.py + guardrail.py +
eval_safety.py together).

    python main.py --target stub                 # fastest, no downloads
    python main.py --target hf --guardrail
"""
import argparse
from target_model import get_target
from red_team import RedTeamGenerator
from eval_safety import report, evaluate_guardrail

def load_goals(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def main(args):
    target = get_target(args.target)
    generator = RedTeamGenerator(target)
    goals = load_goals(args.goals)

    results = generator.generate_batch(goals)
    df = report(results, save=args.out)

    if args.guardrail:
        from guardrail import KeywordGuardrail
        gr = KeywordGuardrail()
        evaluate_guardrail(gr, results)
        print("(Using the lightweight KeywordGuardrail; pass --hf_guardrail "
              "to instead load the transformer-based SafetyGuardrail, which "
              "needs a model download.)")

    if args.hf_guardrail:
        from guardrail import SafetyGuardrail
        gr = SafetyGuardrail()
        evaluate_guardrail(gr, results)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", choices=["stub", "hf", "openai"], default="stub")
    p.add_argument("--goals", default="data/goals.txt")
    p.add_argument("--out", default="safety_report.csv")
    p.add_argument("--guardrail", action="store_true", help="evaluate the keyword guardrail")
    p.add_argument("--hf_guardrail", action="store_true", help="evaluate the transformer guardrail")
    main(p.parse_args())
