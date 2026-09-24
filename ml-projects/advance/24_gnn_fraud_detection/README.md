# 24 Gnn Fraud Detection -- Level 1

Graph Neural Network for fraud/anomaly detection over a transaction graph.

## What's here
- `src/make_data.py` - generates a synthetic transactions dataset (no
  real dataset was included) with an injected, learnable fraud pattern
- `src/graph_builder.py` - builds the transaction graph with normalized
  features and train/val/test **masks** (previously there was no split
  at all -- the model was evaluated on its own training data)
- `src/gnn_model.py` - `FraudGAT` and `FraudGraphSAGE`
- `src/train.py` - trains with class-imbalance weighting, reports F1
  **and AUC** on held-out data, checkpoints the best-val model

## Run
```bash
pip install -r ../requirements.txt
python src/make_data.py --n_users 200 --n_tx 5000
python src/train.py --model gat --epochs 100
```
