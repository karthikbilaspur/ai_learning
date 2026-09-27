# 🔬 10 Advanced ML Projects - From Research to Production

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Level-Advanced%20%7C%20L1%20Fixed-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Projects-21--30-6c5ce7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Research-SimCLR%20%7C%20FL%20%7C%20NAS%20%7C%20GNN%20%7C%20RLHF-black?style=for-the-badge" />
</p>

<p align="center">
  <b>Not tutorials. Real research implementations, fixed to actually run.</b><br>
  Self-Supervised Learning, Federated Learning + DP, NAS, GNN Fraud, LLM Eval, Diffusion, RAG Time Series, RLHF, Edge AI, and AI Safety Red Teaming.
</p>

<p align="center">
  <a href="https://github.com/karthikbilaspur">GitHub: @karthikbilaspur</a> •
  <a href="https://github.com/karthikbilaspur/ai_learning/tree/main/ml-projects/advanced">View on GitHub</a>
</p>

---

## 📚 Projects (21-30)

| # | Project | Entry Point | Needs Network? | Core Concept |
| :--- | :--- | :--- | :--- | :--- |
| **21** | **Self-Supervised Contrastive (SimCLR)** | `src/train.py`, `src/eval_linear.py` | CIFAR-10 download | ResNet-18 (CIFAR-sized), Linear Probe Eval |
| **22** | **Federated Learning + DP** | `src/main.py` (sim) or `src/server.py`+`src/client.py` | CIFAR-10 download | FedAvg, FedProx, DP-SGD Wrapper |
| **23** | **Neural Architecture Search** | `src/controller.py` | MNIST download | RNN Controller, Multi-Objective Search |
| **24** | **GNN Fraud Detection** | `src/make_data.py` then `src/train.py` | **No** - Synthetic | Synthetic Graph, GNN Link Prediction |
| **25** | **LLM Eval Harness** | `src/main.py` | Model-dependent | Accuracy, Calibration, Toxicity, Latency |
| **26** | **Synthetic Data Diffusion** | `src/make_data.py`, `src/train.py`, `src/generate.py`, `src/evaluate_synthetic.py` | **No** - Synthetic | DDPM, Conditional Diffusion |
| **27** | **Retrieval-Augmented Time Series** | `src/make_data.py` then `src/train.py` | **No** - Synthetic | RAG + Transformer Forecaster |
| **28** | **Reward Model for RLHF** | `src/make_data.py` then `src/train_rm.py` | Small HF model | Pairwise Preference, DPO-ready |
| **29** | **Quantization / Pruning / Edge** | `src/main.py` | Small HF model | INT8, Structured Pruning, Edge Bench |
| **30** | **AI Safety Red Teaming** | `src/main.py --target stub` | **No** (`--target stub`); HF/OpenAI optional | ASR, Structured Safety Suite |

---

## 🚀 Setup

This is a research-grade codebase. We trimmed `requirements.txt` to **only what the code actually imports**.

Original file listed `mlflow`, `wandb`, `sdv`, `nni`, `dgl`, `fastapi`, `qdrant-client`, etc. that nothing used. Now it's clean.

```bash
pip install -r requirements.txt
```

> **Offline-first:** Projects 24, 26, 27, 28, 30 (with `--target stub`) run 100% offline with synthetic data. No API keys needed to start.

---

## 🛠️ What "Level 1 Fixed" Means

Each project's own README documents its specific fixes, but these were the recurring gaps closed across all 10:

**1. No Data → Now has Data**
Every project that needed data now ships `make_data.py` that generates a small, structured synthetic dataset or wires up a standard public one (CIFAR-10/MNIST already used by 21/23).

**2. No Config → Now Configurable**
Added `argparse` CLIs and where useful, a `config.py`. No more hardcoded hyperparameters.

**3. No Checkpointing → Now Saves**
Training scripts now save best/last model to `checkpoints/`.

**4. No Real Evaluation → Now Real Metrics**
Added held-out train/val/test splits and the metric each project's README actually promised (F1/AUC, linear-probe accuracy, pairwise preference accuracy, MAE, ASR, etc.) instead of reporting training loss as only signal.

**5. Gated Models → Open Defaults**
Swapped hardcoded gated checkpoints (`meta-llama/Meta-Llama-3-8B`, `meta-llama/Llama-Guard-3-8B`) for small open equivalents (`distilgpt2`, `unitary/toxic-bert`) by default, with comment on how to swap back if you have access.
Project 21's ResNet-50 stem was also swapped for ResNet-18 sized for CIFAR-32 input.

**6. Stub / No-op Functions → Working Code**
`structured_prune_heads()` (29) and `strategy.py` DP wrapper (22) had empty bodies; both now have working implementations.

**7. Disconnected Pieces → End-to-End**
Added a `main.py` per project (where one didn't exist) that actually chains modules together end-to-end.

---

## ✅ Testing

Fast offline smoke test + full test with downloads:

```bash
# Fast, offline - checks py_compile + runs synthetic data gen for 24/26/27/28 and full run of 30 with --target stub
bash tests/smoke_test.sh

# Full - also attempts model/dataset downloads and training (needs network)
bash tests/smoke_test.sh --full
```

The smoke test does **not** attempt anything that needs a model/dataset download by default.

---

## ⬆️ Level-2 Upgrade Path

See `LEVEL2_UPGRADE_GUIDE.md`

Level-2 adds:
- Stronger baselines & ablation/benchmark scaffolding
- Leakage-safe splits
- Multi-objective NAS
- FedProx / privacy diagnostics
- Conditional diffusion
- Transformer forecasting
- DPO
- Compression benchmarking
- Structured safety evaluation suite

This is where you go from "runs" to "publishable / production-ready".

---

## 🧠 Who Is This For?

- **ML Engineers** moving from beginner/intermediate to research implementation
- **MLOps / Edge AI** - Project 29 (Quant/Prune) + 22 (Federated)
- **LLM / Safety** - Projects 25, 28, 30 are direct interview material for LLM teams
- **Recruiters** - If you can explain SimCLR (21), FedAvg+DP (22), and Reward Modeling (28), you're senior ML.

This is **Part 3** of the roadmap:
- **Part 1:** 10 Beginner Projects (01-10)
- **Part 2:** 10 Intermediate Projects (11-20)
- **Part 3:** 10 Advanced Projects (21-30) ← You are here

---

## 👨‍💻 Author

**Karthik Bilaspur**
- GitHub: [@karthikbilaspur](https://github.com/karthikbilaspur)
- Repo: [ai_learning/ml-projects/advanced](https://github.com/karthikbilaspur/ai_learning/tree/main/ml-projects/advanced)

Give a ⭐ if this saved you hours of debugging gated models and empty stubs!

## 📄 License

MIT License - Use for learning, research, and portfolio.
