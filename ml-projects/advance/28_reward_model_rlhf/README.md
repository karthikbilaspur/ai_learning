# 28 Reward Model Rlhf -- Level 1

Reward Model training for RLHF (Bradley-Terry preference loss).

## What's here
- `src/make_data.py` - generates synthetic (prompt, chosen, rejected)
  preference pairs (none was included)
- `src/reward_model.py` - default base model swapped from the gated
  `meta-llama/Meta-Llama-3-8B` to open `distilgpt2`; pooling fixed to
  use the last **non-padded** token per sequence instead of always index `-1`
- `src/train_rm.py` - runs on CPU or GPU (was hard-coded `.cuda()`),
  added a train/val split and **pairwise preference accuracy** as the
  real eval metric, checkpoints the best-val model

## Run
```bash
pip install -r ../requirements.txt
python src/make_data.py --n 500
python src/train_rm.py --jsonl data/preferences.jsonl --base distilgpt2
```
