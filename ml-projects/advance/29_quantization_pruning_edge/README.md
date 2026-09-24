# 29 Quantization Pruning Edge -- Level 1

Model Quantization, Pruning & Distillation for edge deployment.

## What's here
- `src/quantize.py` - default model swapped from gated Llama-3-8B to open `distilgpt2`
- `src/prune.py` - `structured_prune_heads()` **implemented** (previously
  an empty `pass` stub): ranks attention heads by output-projection norm
  and prunes the weakest per layer via HF's `prune_heads()` API
- `src/benchmark.py` - labeled latency/memory measurements
- `src/main.py` - **new**: chains baseline benchmark -> prune ->
  benchmark again -> prints a before/after comparison table (previously
  these were disconnected utilities with nothing wiring them together)

## Run
```bash
pip install -r ../requirements.txt
python src/main.py --model_id distilgpt2 --prune_amount 0.3
```
