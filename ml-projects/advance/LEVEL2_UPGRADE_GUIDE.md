# Level 2 Upgrade — Projects 21–30

The repository remains runnable as a Level-1 collection, while each project now has a Level-2 path focused on **controlled experiments, stronger baselines, leakage prevention, metrics, and reproducibility**.

## Shared infrastructure
- `common/experiment.py`: deterministic seeds, JSON result persistence, lightweight timing.
- Prefer storing every experiment as JSON/CSV under `results/` and recording dataset/model/config/seed.

## Project upgrades

### 21 — SSL
Use `src/ssl_baselines.py` to create a SimCLR temperature-ablation plan and the included SimSiam implementation. Report linear-probe accuracy, kNN accuracy, training time and memory.

### 22 — Federated learning
`src/fedprox.py` adds the proximal local objective; `src/privacy.py` provides an explicitly approximate RDP-style privacy estimate; `src/benchmark_fl.py` creates an IID/non-IID × FedAvg/FedProx × DP matrix. Do not present the approximate epsilon as a formal guarantee without a validated accountant.

### 23 — NAS
`src/multiobjective.py` searches accuracy, parameter count and CPU latency simultaneously and exposes the Pareto frontier.

### 24 — fraud GNN
`src/temporal_graph.py` makes the split chronological, reducing future-information leakage. `src/metrics.py` adds F1, ROC-AUC and PR-AUC. The next experiment should replace the simple graph with a heterogeneous customer/account/device/merchant graph.

### 25 — LLM evaluation
`src/benchmark.py` adds repeated evaluation and latency statistics; `src/regression.py` compares two metric JSON files. The next step is a persistent evaluation dataset and CI regression gate.

### 26 — diffusion
`src/conditional.py` adds conditional denoising; `src/baselines.py` adds a Gaussian baseline; `src/evaluate_tradeoff.py` reports fidelity, utility retention and nearest-neighbour distance together.

### 27 — time series
`src/transformer_forecaster.py` provides a direct Transformer baseline; `src/benchmark.py` standardizes MAE/RMSE/sMAPE and chronological splits. Compare LSTM, Transformer and retrieval-augmented Transformer using a training-only retrieval corpus.

### 28 — preference optimization
`src/dpo.py` provides the DPO objective; `src/preference_diagnostics.py` checks reward/length correlation and chosen-vs-rejected margins. Compare SFT, reward-model reranking and DPO.

### 29 — compression
`src/compression_benchmark.py` compares FP32, dynamic INT8 and 50% magnitude pruning on CPU. Report latency, parameter count, sparsity and memory. For true edge claims, repeat on target hardware.

### 30 — safety
`src/attack_suite.py` defines benign evaluation families; `src/safety_metrics.py` separates refusal and guardrail error rates; `src/run_level2.py` runs the matrix. Treat refusal heuristics as a proxy and add a stronger safety judge before making research claims.

## Level-2 acceptance criteria
Every project should have:
1. At least one meaningful baseline.
2. One controlled ablation.
3. At least three relevant metrics.
4. A fixed seed and explicit data split.
5. A saved machine-readable result file.
6. Failure analysis in the README.
7. No train/test or future-data leakage.
8. A reproducible command from a clean environment.
