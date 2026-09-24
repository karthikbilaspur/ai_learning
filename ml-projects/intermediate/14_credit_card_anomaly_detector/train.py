"""
Level 2 upgrade — Credit Card Spending Anomaly Detector
- Uses the injected ground-truth labels to report real precision/recall/F1
  and PR-AUC instead of only printing counts (the level-1 version never
  scored itself against the anomalies it created).
- Compares Isolation Forest, One-Class SVM and Local Outlier Factor.
- Richer feature set (amount, hour, distance, merchant-category risk,
  transaction velocity) and a larger, noisier dataset.
- Saves a threshold-tunable anomaly score, not just a hard label.

NOTE: this project's natural real-data upgrade is the Kaggle "Credit Card
Fraud Detection" dataset (284k transactions, ~150MB) — the pipeline below
is written so you can swap `make_data()` for `pd.read_csv("creditcard.csv")`
with matching column names and rerun unchanged.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, precision_recall_curve, auc, roc_auc_score
)
import matplotlib.pyplot as plt
import joblib

RANDOM_STATE = 42


def make_data(n_normal=4000, n_anomaly=120):
    rng = np.random.default_rng(RANDOM_STATE)
    normal = pd.DataFrame({
        "amount": rng.lognormal(3.5, 0.6, n_normal),
        "hour": rng.integers(7, 23, n_normal),
        "distance_km": rng.exponential(4, n_normal),
        "merchant_risk": rng.beta(1.5, 6, n_normal),          # most merchants low-risk
        "txns_last_hour": rng.poisson(1.2, n_normal),
    })
    anomalies = pd.DataFrame({
        "amount": rng.uniform(800, 5000, n_anomaly),
        "hour": rng.integers(0, 6, n_anomaly),
        "distance_km": rng.uniform(80, 800, n_anomaly),
        "merchant_risk": rng.beta(4, 2, n_anomaly),           # riskier merchants
        "txns_last_hour": rng.poisson(5, n_anomaly),
    })
    df = pd.concat([normal, anomalies], ignore_index=True)
    df["is_fraud"] = [0] * n_normal + [1] * n_anomaly
    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def evaluate(name, scores_higher_is_anomalous, y_true):
    """scores_higher_is_anomalous: higher score => more anomalous."""
    precision, recall, _ = precision_recall_curve(y_true, scores_higher_is_anomalous)
    pr_auc = auc(recall, precision)
    roc_auc = roc_auc_score(y_true, scores_higher_is_anomalous)
    print(f"{name}: PR-AUC={pr_auc:.3f}  ROC-AUC={roc_auc:.3f}")
    return pr_auc, roc_auc


def main():
    df = make_data()
    features = ["amount", "hour", "distance_km", "merchant_risk", "txns_last_hour"]
    X = df[features]
    y = df["is_fraud"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    contamination = y.mean()

    iso = IsolationForest(n_estimators=300, contamination=contamination, random_state=RANDOM_STATE)
    iso.fit(Xs)
    iso_scores = -iso.score_samples(Xs)  # higher = more anomalous

    ocsvm = OneClassSVM(nu=contamination, kernel="rbf", gamma="scale")
    ocsvm.fit(Xs)
    ocsvm_scores = -ocsvm.decision_function(Xs)

    lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination, novelty=False)
    lof_labels = lof.fit_predict(Xs)
    lof_scores = -lof.negative_outlier_factor_

    print("Model comparison (ranked by how well the anomaly score separates real fraud):")
    results = {}
    for name, scores in [("isolation_forest", iso_scores), ("one_class_svm", ocsvm_scores), ("local_outlier_factor", lof_scores)]:
        results[name] = evaluate(name, scores, y)

    best_name = max(results, key=lambda k: results[k][0])
    print(f"\nBest model by PR-AUC: {best_name}")

    df["anomaly_score"] = iso_scores  # keep Isolation Forest as the deployed model (fit_predict on new data)
    threshold = np.quantile(iso_scores, 1 - contamination)
    df["flagged"] = df["anomaly_score"] >= threshold

    print("\nIsolation Forest classification report at the contamination-matched threshold:")
    print(classification_report(y, df["flagged"].astype(int)))

    plt.figure(figsize=(6, 5))
    for name, scores in [("isolation_forest", iso_scores), ("one_class_svm", ocsvm_scores), ("local_outlier_factor", lof_scores)]:
        precision, recall, _ = precision_recall_curve(y, scores)
        plt.plot(recall, precision, label=name)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall curves")
    plt.legend()
    plt.tight_layout()
    plt.savefig("pr_curves.png")
    plt.close()

    df.to_csv("transactions_with_anomaly_flags.csv", index=False)
    joblib.dump({"scaler": scaler, "model": iso, "features": features, "threshold": threshold}, "anomaly_model.joblib", compress=3)
    print("\nSaved: anomaly_model.joblib, transactions_with_anomaly_flags.csv, pr_curves.png")


if __name__ == "__main__":
    main()
