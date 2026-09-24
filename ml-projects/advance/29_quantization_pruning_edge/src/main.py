"""End-to-end compression pipeline: load a small open model, benchmark
it, magnitude-prune it, benchmark again, and print a before/after
comparison table (previously prune/distill/quantize/benchmark existed as
disconnected utilities with nothing wiring them together).

    python main.py --model_id distilgpt2 --prune_amount 0.3
"""
import argparse
from transformers import AutoModel, AutoTokenizer

from benchmark import benchmark
from prune import magnitude_prune, check_sparsity

def main(args):
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModel.from_pretrained(args.model_id)

    print("=== Baseline ===")
    baseline = benchmark(model, tokenizer, prompt=args.prompt, label="baseline")
    check_sparsity(model)

    print("\n=== After magnitude pruning ===")
    model = magnitude_prune(model, amount=args.prune_amount)
    pruned = benchmark(model, tokenizer, prompt=args.prompt, label=f"pruned_{args.prune_amount}")
    sparsity = check_sparsity(model)

    print("\n=== Summary ===")
    print(f"{'':12s} {'latency (ms)':>14s} {'mem (MB)':>10s}")
    print(f"{'baseline':12s} {baseline['latency_ms']:14.1f} {baseline['mem_mb']:10.1f}")
    print(f"{'pruned':12s} {pruned['latency_ms']:14.1f} {pruned['mem_mb']:10.1f}")
    print(f"Sparsity after pruning: {sparsity:.1f}%")
    print("\nNote: unstructured magnitude pruning zeroes weights but does not\n"
          "shrink tensors, so latency/memory won't drop without a sparse\n"
          "runtime or actually removing structured units -- see\n"
          "structured_prune_heads() in prune.py for a latency-reducing option.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model_id", default="distilgpt2")
    p.add_argument("--prompt", default="Hello world, this is a benchmark.")
    p.add_argument("--prune_amount", type=float, default=0.3)
    main(p.parse_args())
