"""
Level 2 upgrade — Traffic Accident Severity Prediction
- Severity is ordered (low < medium < high), so alongside a standard
  multi-class Random Forest this adds an ordinal baseline (cumulative
  logistic regression via multiple binary "is severity >= threshold"
  classifiers) and compares them — misclassifying high as low is a worse
  mistake than high as medium, which plain multi-class accuracy ignores.
- Reports per-class precision/recall (catching "high" severity matters most).
- Adds geographic-style clustering feature (simulated road-segment risk)
  and time-of-day/seasonal interaction.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import joblib

RANDOM_STATE = 42


def make_data(n=3500):
    rng = np.random.default_rng(RANDOM_STATE)
    df = pd.DataFrame({
        "speed_limit": rng.choice([30, 40, 50, 60, 80, 100], n),
        "rain_mm": rng.exponential(2, n),
        "visibility_km": rng.uniform(0.5, 15, n),
        "traffic_density": rng.uniform(0, 1, n),
        "night": rng.integers(0, 2, n),
        "road_risk_score": rng.beta(2, 5, n),  # stand-in for a geographic hotspot feature
    })
    df["is_weekend"] = rng.integers(0, 2, n)

    risk = (
        0.03 * df.speed_limit + 0.08 * df.rain_mm
        - 0.12 * df.visibility_km + 0.9 * df.traffic_density
        + 0.5 * df.night + 1.5 * df.road_risk_score
        + 0.2 * df.night * df.is_weekend
        + rng.normal(0, 0.7, n)
    )
    df["severity"] = pd.qcut(risk, q=3, labels=["low", "medium", "high"])
    return df


class OrdinalClassifier:
    """Fits K-1 binary classifiers for P(severity >= k) and derives class probabilities."""

    def __init__(self, base_estimator, classes):
        self.base_estimator = base_estimator
        self.classes = classes  # ordered, e.g. ["low", "medium", "high"]
        self.models = []

    def fit(self, X, y):
        from sklearn.base import clone
        y_idx = pd.Categorical(y, categories=self.classes, ordered=True).codes
        self.models = []
        for k in range(1, len(self.classes)):
            binary_y = (y_idx >= k).astype(int)
            model = clone(self.base_estimator)
            model.fit(X, binary_y)
            self.models.append(model)
        return self

    def predict(self, X):
        # P(y >= k) for each threshold model
        p_ge = np.column_stack([m.predict_proba(X)[:, 1] for m in self.models])
        p_ge = np.hstack([np.ones((len(X), 1)), p_ge, np.zeros((len(X), 1))])
        class_probs = -np.diff(p_ge, axis=1)  # P(y = k) = P(y>=k) - P(y>=k+1)
        idx = np.argmax(class_probs, axis=1)
        return np.array(self.classes)[idx]


def main():
    df = make_data()
    features = ["speed_limit", "rain_mm", "visibility_km", "traffic_density", "night", "road_risk_score", "is_weekend"]
    X = df[features]
    y = df["severity"]
    class_order = ["low", "medium", "high"]

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    rf = RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=RANDOM_STATE)
    rf.fit(Xtr, ytr)
    pred_rf = rf.predict(Xte)

    ordinal = OrdinalClassifier(
        LogisticRegression(max_iter=1000, class_weight="balanced"), class_order
    )
    ordinal.fit(Xtr, ytr)
    pred_ord = ordinal.predict(Xte)

    print("=== Random Forest (plain multi-class) ===")
    print(classification_report(yte, pred_rf))
    print("Macro F1:", round(f1_score(yte, pred_rf, average="macro"), 3))

    print("\n=== Ordinal logistic (respects low<medium<high ordering) ===")
    print(classification_report(yte, pred_ord))
    print("Macro F1:", round(f1_score(yte, pred_ord, average="macro"), 3))

    # How often does each model mistake "high" for "low" (the costly error)?
    def high_as_low_rate(y_true, y_pred):
        mask = np.array(y_true) == "high"
        if mask.sum() == 0:
            return 0.0
        return float(np.mean(np.array(y_pred)[mask] == "low"))

    print(f"\nP(predict 'low' | actual 'high') — Random Forest: {high_as_low_rate(yte, pred_rf):.1%}")
    print(f"P(predict 'low' | actual 'high') — Ordinal model:  {high_as_low_rate(yte, pred_ord):.1%}")

    cm = confusion_matrix(yte, pred_rf, labels=class_order)
    plt.figure(figsize=(5, 4))
    plt.imshow(cm, cmap="Reds")
    plt.xticks(range(3), class_order)
    plt.yticks(range(3), class_order)
    for i in range(3):
        for j in range(3):
            plt.text(j, i, cm[i, j], ha="center", va="center")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion matrix (Random Forest)")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    plt.close()

    joblib.dump({"rf": rf, "ordinal": ordinal, "features": features}, "severity_model.joblib", compress=3)
    print("\nSaved: severity_model.joblib, confusion_matrix.png")


if __name__ == "__main__":
    main()
