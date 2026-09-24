"""Generates a small synthetic (prompt, chosen, rejected) preference
dataset so the reward model has something to train on out-of-the-box.

    python make_data.py --n 500
"""
import argparse, json, random

PROMPTS = [
    "Explain how photosynthesis works.",
    "Write a short poem about the ocean.",
    "What's a healthy breakfast idea?",
    "Give me tips for public speaking.",
    "Summarize the water cycle.",
    "Describe how a car engine works.",
    "Suggest a weekend trip itinerary.",
    "How do I start learning to code?",
]

GOOD_SUFFIXES = [
    " Here is a clear, accurate, and helpful answer: {}",
    " Sure, happy to help -- {}",
]
BAD_SUFFIXES = [
    " idk lol not sure, maybe {}?? whatever",
    " {} (this is deliberately vague and unhelpful)",
]

def make_example(prompt, seed):
    rng = random.Random(seed)
    body = f"detail #{rng.randint(1,999)}"
    chosen = rng.choice(GOOD_SUFFIXES).format(body)
    rejected = rng.choice(BAD_SUFFIXES).format(body)
    return {"prompt": prompt, "chosen": chosen, "rejected": rejected}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=500)
    p.add_argument("--out", default="data/preferences.jsonl")
    args = p.parse_args()
    rng = random.Random(42)
    with open(args.out, "w") as f:
        for i in range(args.n):
            prompt = rng.choice(PROMPTS)
            ex = make_example(prompt, seed=i)
            f.write(json.dumps(ex) + "\n")
    print(f"Wrote {args.n} preference pairs to {args.out}")
