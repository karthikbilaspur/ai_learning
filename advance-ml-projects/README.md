# advance-ml-projects (21-30) -- Level 1

10 advanced ML projects, upgraded from bare skeletons ("Level 2") to
runnable, end-to-end pipelines ("Level 1"): every project now has real
data (generated locally, or a standard public dataset), a training/run
script with CLI args and checkpointing, and an evaluation step with
actual metrics -- not just a loss printout.

## Projects
| # | Project | Entry point | Needs network? |
|---|---|---|---|
| 21 | Self-Supervised Contrastive (SimCLR) | `src/train.py`, `src/eval_linear.py` | CIFAR-10 download |
| 22 | Federated Learning + DP | `src/main.py` (simulation) or `src/server.py`+`src/client.py` | CIFAR-10 download |
| 23 | Neural Architecture Search | `src/controller.py` | MNIST download |
| 24 | GNN Fraud Detection | `src/make_data.py` then `src/train.py` | none (synthetic data) |
| 25 | LLM Eval Harness | `src/main.py` | model-dependent (see below) |
| 26 | Synthetic Data Diffusion | `src/make_data.py`, `src/train.py`, `src/generate.py`, `src/evaluate_synthetic.py` | none (synthetic data) |
| 27 | Retrieval-Augmented Time Series | `src/make_data.py` then `src/train.py` | none (synthetic data) |
| 28 | Reward Model for RLHF | `src/make_data.py` then `src/train_rm.py` | small HF model download |
| 29 | Quantization/Pruning/Edge | `src/main.py` | small HF model download |
| 30 | AI Safety Red Teaming | `src/main.py --target stub` | none (`--target stub`); HF/OpenAI optional |

## Setup
```bash
pip install -r requirements.txt
```
`requirements.txt` was trimmed to only what the code actually imports
(the original listed several libraries -- `mlflow`, `wandb`, `sdv`,
`nni`, `dgl`, `fastapi`, `qdrant-client`, etc. -- that nothing in the
codebase used).

## What "Level 1" means here
Each project's own README documents its specific fixes, but the
recurring gaps closed across all 10 were:
- **No data**: every project that needed data now ships a
  `make_data.py` that generates a small, structured synthetic dataset
  (or wires up a standard public one, e.g. CIFAR-10/MNIST already used
  by 21/23).
- **No config / all-hardcoded hyperparameters**: added `argparse` CLIs
  and, where useful, a `config.py`.
- **No checkpointing**: training scripts now save the best/last model
  to `checkpoints/`.
- **No real evaluation**: added held-out train/val/test splits and the
  metric each project's README actually promised (F1/AUC, linear-probe
  accuracy, pairwise preference accuracy, MAE, ASR, etc.) instead of
  reporting training loss as the only signal.
- **Gated models**: swapped hardcoded gated checkpoints
  (`meta-llama/Meta-Llama-3-8B`, `meta-llama/Llama-Guard-3-8B`) for
  small open equivalents (`distilgpt2`, `unitary/toxic-bert`) by
  default, with a comment on how to swap back if you have access.
  Project 21's ResNet-50 stem was also swapped for a ResNet-18 sized
  for CIFAR-32 input.
- **Stub/no-op functions**: `structured_prune_heads()` (29) and the
  `strategy.py` DP wrapper (22) had empty bodies; both now have working
  implementations.
- **Disconnected pieces**: added a `main.py` per project (where one
  didn't exist) that actually chains the modules together end-to-end.

## Testing
`tests/smoke_test.sh` runs `py_compile` on every file and actually
executes the offline, dependency-light parts (synthetic data generation
for 24/26/27/28, and a full run of 30 with `--target stub`). It does
**not** attempt anything that needs a model/dataset download by
default -- pass `--full` after installing requirements to also try
those (needs network access).
```bash
bash tests/smoke_test.sh          # fast, offline
bash tests/smoke_test.sh --full   # also attempts downloads/training
```

## Level-2 upgrade
See `LEVEL2_UPGRADE_GUIDE.md`. The Level-2 work adds stronger baselines, ablation/benchmark scaffolding, leakage-safe splits, multi-objective NAS, FedProx/privacy diagnostics, conditional diffusion, Transformer forecasting, DPO, compression benchmarking, and a structured safety evaluation suite.
