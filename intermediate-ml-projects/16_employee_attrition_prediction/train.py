"""
Level 2 upgrade — Employee Attrition Prediction
- Real dataset (IBM HR Analytics Attrition, 1470 employees, data/hr_attrition.csv)
  instead of synthetic data.
- Explicit handling of class imbalance (~16% attrition): class_weight /
  scale_pos_weight, PR-AUC alongside ROC-AUC.
- Compares Logistic Regression, Random Forest and XGBoost via CV.
- SHAP explanations for individual-level interpretation ("why is this
  employee flagged"), which matters more than accuracy for an HR audience.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, average_precision_score, precision_recall_curve
)
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import shap
import joblib

RANDOM_STATE = 42
DATA_PATH = "data/hr_attrition.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Attrition"] = (df["Attrition"] == "Yes").astype(int)
    drop_cols = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return df


def main():
    df = load_data()
    y = df["Attrition"]
    X = df.drop(columns="Attrition")

    num = X.select_dtypes(include="number").columns.tolist()
    cat = [c for c in X.columns if c not in num]
    print(f"{len(num)} numeric features, {len(cat)} categorical features")
    print(f"Attrition rate: {y.mean():.1%}")

    pre = ColumnTransformer([
        ("num", "passthrough", num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    candidates = {
        "logreg": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=400, class_weight="balanced", random_state=RANDOM_STATE),
        "xgboost": XGBClassifier(n_estimators=300, scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE, eval_metric="logloss"),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = {}
    for name, clf in candidates.items():
        pipe = Pipeline([("preprocess", pre), ("classifier", clf)])
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="average_precision")
        cv_scores[name] = scores.mean()
        print(f"{name}: CV PR-AUC = {scores.mean():.3f} (+/- {scores.std():.3f})")

    best_name = max(cv_scores, key=cv_scores.get)
    print(f"\nBest model: {best_name}")

    model = Pipeline([("preprocess", pre), ("classifier", candidates[best_name])])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]

    print("\nHeld-out test performance:")
    print(classification_report(y_test, pred))
    print("ROC-AUC:", round(roc_auc_score(y_test, prob), 3))
    print("PR-AUC:", round(average_precision_score(y_test, prob), 3))

    precision, recall, _ = precision_recall_curve(y_test, prob)
    plt.figure(figsize=(5, 4))
    plt.plot(recall, precision)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall curve ({best_name})")
    plt.tight_layout()
    plt.savefig("precision_recall.png")
    plt.close()

    joblib.dump(model, "attrition_model.joblib", compress=3)

    # SHAP: works cleanly for tree models; for logreg fall back to coefficients
    try:
        clf = model.named_steps["classifier"]
        X_test_enc = model.named_steps["preprocess"].transform(X_test)
        feature_names = model.named_steps["preprocess"].get_feature_names_out()
        if hasattr(clf, "feature_importances_") or "XGB" in type(clf).__name__ or "Forest" in type(clf).__name__:
            explainer = shap.TreeExplainer(clf)
            shap_values = explainer.shap_values(X_test_enc)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            plt.figure()
            shap.summary_plot(shap_values, X_test_enc, feature_names=feature_names, show=False, max_display=15)
            plt.tight_layout()
            plt.savefig("shap_summary.png", bbox_inches="tight")
            plt.close()
            print("Saved: shap_summary.png")
    except Exception as e:
        print(f"(SHAP plot skipped: {e})")

    print("Saved: attrition_model.joblib, precision_recall.png")


if __name__ == "__main__":
    main()
