"""
Level 2 upgrade — Used Car Price Prediction
- Real dataset (CarPrice_Assignment.csv, 205 US-market cars) instead of
  synthetic data.
- Extracts car brand from CarName (with typo cleanup, e.g. "maxda" -> "mazda").
- Compares Random Forest, Gradient Boosting and XGBoost via 5-fold CV.
- Hyperparameter tuning (RandomizedSearchCV) for the winning model.
- SHAP explanations for individual predictions.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import shap
import joblib

RANDOM_STATE = 42
DATA_PATH = "data/CarPrice_Assignment.csv"

BRAND_FIXES = {
    "maxda": "mazda", "porcshce": "porsche", "toyouta": "toyota",
    "vokswagen": "volkswagen", "vw": "volkswagen", "Nissan": "nissan",
}


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["brand"] = df["CarName"].str.split().str[0].str.lower()
    df["brand"] = df["brand"].replace(BRAND_FIXES)
    return df


def main():
    df = load_data()

    num = ["symboling", "wheelbase", "carlength", "carwidth", "carheight", "curbweight",
           "enginesize", "boreratio", "stroke", "compressionratio", "horsepower",
           "peakrpm", "citympg", "highwaympg"]
    cat = ["brand", "fueltype", "aspiration", "doornumber", "carbody", "drivewheel",
           "enginelocation", "enginetype", "cylindernumber", "fuelsystem"]

    X = df[num + cat]
    y = df["price"]

    pre = ColumnTransformer([
        ("num", "passthrough", num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    candidates = {
        "random_forest": RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "xgboost": XGBRegressor(n_estimators=300, random_state=RANDOM_STATE, verbosity=0),
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = {}
    for name, reg in candidates.items():
        pipe = Pipeline([("preprocess", pre), ("regressor", reg)])
        scores = cross_val_score(pipe, X_train, y_train, cv=kf, scoring="neg_mean_absolute_error")
        cv_scores[name] = -scores.mean()
        print(f"{name}: CV MAE = {-scores.mean():.1f} (+/- {scores.std():.1f})")

    best_name = min(cv_scores, key=cv_scores.get)
    print(f"\nBest model: {best_name}")

    # Light hyperparameter tuning for the winner
    param_grids = {
        "random_forest": {
            "regressor__n_estimators": [200, 300, 500],
            "regressor__max_depth": [None, 8, 12, 20],
            "regressor__min_samples_leaf": [1, 2, 4],
        },
        "gradient_boosting": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__learning_rate": [0.03, 0.05, 0.1],
            "regressor__max_depth": [2, 3, 4],
        },
        "xgboost": {
            "regressor__n_estimators": [200, 300, 500],
            "regressor__learning_rate": [0.03, 0.05, 0.1],
            "regressor__max_depth": [3, 4, 6],
        },
    }
    base_pipe = Pipeline([("preprocess", pre), ("regressor", candidates[best_name])])
    search = RandomizedSearchCV(
        base_pipe, param_grids[best_name], n_iter=8, cv=kf,
        scoring="neg_mean_absolute_error", random_state=RANDOM_STATE, n_jobs=-1
    )
    search.fit(X_train, y_train)
    model = search.best_estimator_
    print("Best params:", search.best_params_)

    pred = model.predict(X_test)
    print("\nHeld-out test performance:")
    print("MAE:", round(mean_absolute_error(y_test, pred), 1))
    print("RMSE:", round(root_mean_squared_error(y_test, pred), 1))
    print("R2:", round(r2_score(y_test, pred), 3))

    joblib.dump(model, "used_car_price_model.joblib", compress=3)
    joblib.dump({"num": num, "cat": cat}, "feature_spec.joblib", compress=3)

    # SHAP explanation (tree-based models only)
    try:
        X_test_enc = model.named_steps["preprocess"].transform(X_test)
        feature_names = model.named_steps["preprocess"].get_feature_names_out()
        explainer = shap.TreeExplainer(model.named_steps["regressor"])
        shap_values = explainer.shap_values(X_test_enc)

        plt.figure()
        shap.summary_plot(shap_values, X_test_enc, feature_names=feature_names, show=False, max_display=12)
        plt.tight_layout()
        plt.savefig("shap_summary.png", bbox_inches="tight")
        plt.close()
        print("Saved: shap_summary.png")
    except Exception as e:
        print(f"(SHAP plot skipped: {e})")

    print("Saved: used_car_price_model.joblib, feature_spec.joblib")


if __name__ == "__main__":
    main()
