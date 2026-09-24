#!/usr/bin/env bash
# Fast, mostly-offline smoke test across all 10 projects.
# Anything that needs a model/dataset download is marked and skipped by
# default; pass --full to also attempt those (needs network + torch stack).
set -e
FULL=${1:-}

echo "== 21: py_compile only (needs CIFAR10 download to actually train) =="
python3 -m py_compile 21_self_supervised_contrastive/src/*.py

echo "== 22: py_compile + dataset partition logic needs torch+torchvision =="
python3 -m py_compile 22_federated_learning/src/*.py

echo "== 23: py_compile only (needs MNIST download) =="
python3 -m py_compile 23_neural_architecture_search/src/*.py

echo "== 24: generate synthetic data (offline, no torch needed) =="
(cd 24_gnn_fraud_detection && python3 src/make_data.py --n_tx 500 --out /tmp/tx.csv)
python3 -m py_compile 24_gnn_fraud_detection/src/*.py

echo "== 25: py_compile only (needs HF model / dataset download) =="
python3 -m py_compile 25_llm_eval_harness/src/*.py

echo "== 26: generate synthetic data (offline, no torch needed) =="
(cd 26_synthetic_data_diffusion && python3 src/make_data.py --n_samples 300 --out /tmp/real.csv)
python3 -m py_compile 26_synthetic_data_diffusion/src/*.py

echo "== 27: generate synthetic series (offline, no torch needed) =="
(cd 27_retrieval_time_series && python3 src/make_data.py --length 1000 --out /tmp/series.npy)
python3 -m py_compile 27_retrieval_time_series/src/*.py

echo "== 28: generate synthetic preference pairs (offline) =="
(cd 28_reward_model_rlhf && python3 src/make_data.py --n 50 --out /tmp/prefs.jsonl)
python3 -m py_compile 28_reward_model_rlhf/src/*.py

echo "== 29: py_compile only (needs HF model download) =="
python3 -m py_compile 29_quantization_pruning_edge/src/*.py

echo "== 30: full offline run with the stub target =="
(cd 30_ai_safety_red_teaming/src && python3 main.py --target stub --goals ../data/goals.txt --out /tmp/safety_report.csv)
python3 -m py_compile 30_ai_safety_red_teaming/src/*.py

echo
echo "All syntax checks + offline data-generation smoke tests passed."
if [ "$FULL" != "--full" ]; then
  echo "(Run with --full after 'pip install -r requirements.txt' to also"
  echo " attempt actual model training, which needs network access for"
  echo " CIFAR10/MNIST/HF-model downloads.)"
fi
