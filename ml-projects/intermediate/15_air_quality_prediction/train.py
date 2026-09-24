"""
Level 2 upgrade — Air Quality Prediction
- Compares Random Forest, Gradient Boosting and XGBoost with 5-fold CV
  (instead of a single train/test split with one fixed model).
- Adds residual diagnostics to check for systematic bias.
- SHAP feature-importance plot.

NOTE: the natural real-data upgrade here is a public hourly air-quality feed
(e.g. UCI Air Quality dataset, or a live OpenAQ/CPCB API pull) reshaped into
a proper time-series problem with lag features — the current version still
treats each hour as an independent row. `make_data()` is isolated so you can
swap it for `pd.read_csv(...)` and keep the rest of the pipeline.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import shap
import joblib

RANDOM_STATE = 42


def make_data(n=3000):
    rng = np.random.default_rng(RANDOM_STATE)
    df = pd.DataFrame({
        "pm25": rng.gamma(3, 12, n),
        "pm10": rng.gamma(3, 20, n),
        "no2": rng.gamma(2, 15, n),
        "so2": rng.gamma(1.5, 8, n),
        "co": rng.gamma(2, 0.6, n),
        "temperature": rng.normal(27, 7, n),
        "humidity": rng.uniform(25, 95, n),
        "wind_speed": rng.gamma(2, 2, n),
    })
    df["air_quality_score"] = (
        100 - 1.2 * df.pm25 - 0.5 * df.pm10 - 0.7 * df.no2 - 0.3 * df.so2 - 4 * df.co
        + 0.08 * df.wind_speed - 0.05 * abs(df.temperature - 25)
        + rng.normal(0, 5, n)
    )
    return df


def main():
    df = make_data()
    X = df.drop(columns="air_quality_score")
    y = df["air_quality_score"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    candidates = {
        "random_forest": RandomForestRegressor(n_estimators=250, random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "xgboost": XGBRegressor(n_estimators=250, random_state=RANDOM_STATE, verbosity=0),
    }
    kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = {}
    for name, model in candidates.items():
        scores = cross_val_score(model, X_train, y_train, cv=kf, scoring="neg_mean_absolute_error")
        cv_scores[name] = -scores.mean()
        print(f"{name}: CV MAE = {-scores.mean():.2f} (+/- {scores.std():.2f})")

    best_name = min(cv_scores, key=cv_scores.get)
    print(f"\nBest model: {best_name}")

    param_grids = {
        "random_forest": {"n_estimators": [200, 300, 500], "max_depth": [None, 8, 15], "min_samples_leaf": [1, 2, 4]},
        "gradient_boosting": {"n_estimators": [100, 200, 300], "learning_rate": [0.03, 0.05, 0.1], "max_depth": [2, 3, 4]},
        "xgboost": {"n_estimators": [200, 300, 500], "learning_rate": [0.03, 0.05, 0.1], "max_depth": [3, 4, 6]},
    }
    search = RandomizedSearchCV(
        candidates[best_name], param_grids[best_name], n_iter=8, cv=kf,
        scoring="neg_mean_absolute_error", random_state=RANDOM_STATE, n_jobs=-1
    )
    search.fit(X_train, y_train)
    model = search.best_estimator_
    print("Best params:", search.best_params_)

    pred = model.predict(X_test)
    print("\nHeld-out test performance:")
    print("MAE:", round(mean_absolute_error(y_test, pred), 2))
    print("R2:", round(r2_score(y_test, pred), 3))

    residuals = y_test - pred
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].scatter(pred, residuals, alpha=0.4, s=10)
    axes[0].axhline(0, color="red", linestyle="--")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Residual")
    axes[0].set_title("Residuals vs predicted (bias check)")
    axes[1].hist(residuals, bins=30)
    axes[1].set_title("Residual distribution")
    plt.tight_layout()
    plt.savefig("residual_diagnostics.png")
    plt.close()

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        plt.figure()
        shap.summary_plot(shap_values, X_test, show=False)
        plt.tight_layout()
        plt.savefig("shap_summary.png", bbox_inches="tight")
        plt.close()
        print("Saved: shap_summary.png")
    except Exception as e:
        print(f"(SHAP plot skipped: {e})")

    joblib.dump(model, "air_quality_model.joblib", compress=3)
    joblib.dump(list(X.columns), "feature_order.joblib", compress=3)
    print("Saved: air_quality_model.joblib, residual_diagnostics.png")


if __name__ == "__main__":
    main()
