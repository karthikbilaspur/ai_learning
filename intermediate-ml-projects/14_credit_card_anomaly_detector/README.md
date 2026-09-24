# 14 - Credit Card Spending Anomaly Detector (Level 2)

Unsupervised anomaly detection, now scored against ground-truth labels.

## What changed from Level 1
- The Level 1 version generated labeled anomalies but never actually scored
  itself against them. This version reports real **precision, recall,
  PR-AUC and ROC-AUC**.
- Compares **Isolation Forest, One-Class SVM, and Local Outlier Factor**.
- Richer feature set: amount, hour, distance from home, merchant risk score,
  transaction velocity (txns in the last hour).
- Interactive Gradio demo (`app.py`).

## Honest limitation
The synthetic anomalies are cleanly separated, so scores look
near-perfect (PR-AUC ≈ 1.0). The natural real-data upgrade is the Kaggle
"Credit Card Fraud Detection" dataset (284k real transactions, ~150MB) —
swap `make_data()` for `pd.read_csv("creditcard.csv")` with matching
columns and rerun; expect much messier, more realistic scores there.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`anomaly_model.joblib`, `transactions_with_anomaly_flags.csv`, `pr_curves.png`

## Level 3 ideas
Autoencoder-based detector; real-time streaming simulation that scores
transactions one at a time as they "arrive".
