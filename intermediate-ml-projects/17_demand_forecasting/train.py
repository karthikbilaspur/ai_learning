"""
Level 2 upgrade — Retail Demand Forecasting
- Adds holiday and promotion flags as calendar features (missing from level 1).
- Walk-forward (rolling-origin) cross-validation instead of one fixed split,
  which is the correct way to validate a time-series model.
- Reports MAPE alongside MAE.
- Adds quantile regression (10th/90th percentile) for a prediction interval,
  not just a point forecast.

NOTE: the natural real-data upgrade is a public retail dataset (Kaggle
M5 / Rossmann / Walmart) with per-store, per-SKU series and hierarchical
reconciliation — this script keeps a single aggregate series but the CV and
feature-engineering approach carries over directly.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
import joblib

RANDOM_STATE = 42


def make_data(n_days=1000):
    rng = np.random.default_rng(RANDOM_STATE)
    dates = pd.date_range("2022-01-01", periods=n_days, freq="D")
    t = np.arange(n_days)

    # holidays: a handful of fixed dates per year + Black Friday-style spike
    holiday_dates = set()
    for year in range(2022, 2026):
        for md in [(1, 1), (7, 4), (11, 25), (12, 25)]:
            holiday_dates.add(pd.Timestamp(year, md[0], md[1]))
    is_holiday = pd.Series(dates).isin(holiday_dates).astype(int).values

    # promotions: random ~8% of days, boosts demand
    is_promo = rng.binomial(1, 0.08, n_days)

    demand = (
        100 + 0.05 * t
        + 15 * np.sin(2 * np.pi * t / 7)
        + 8 * np.sin(2 * np.pi * t / 365)
        + 25 * is_holiday
        + 20 * is_promo
        + rng.normal(0, 5, n_days)
    )

    df = pd.DataFrame({"date": dates, "demand": demand, "is_holiday": is_holiday, "is_promo": is_promo})
    for lag in [1, 7, 14, 28]:
        df[f"lag_{lag}"] = df.demand.shift(lag)
    df["rolling_7"] = df.demand.shift(1).rolling(7).mean()
    df["rolling_28"] = df.demand.shift(1).rolling(28).mean()
    df["dayofweek"] = df.date.dt.dayofweek
    df["month"] = df.date.dt.month
    return df.dropna().reset_index(drop=True)


def walk_forward_cv(df, features, n_splits=5, test_size=60):
    """Rolling-origin CV: train on everything before a cut, test on the next block."""
    maes = []
    n = len(df)
    for i in range(n_splits):
        cut = n - test_size * (n_splits - i)
        train = df.iloc[:cut]
        test = df.iloc[cut: cut + test_size]
        if len(test) == 0:
            continue
        model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=RANDOM_STATE)
        model.fit(train[features], train.demand)
        pred = model.predict(test[features])
        maes.append(mean_absolute_error(test.demand, pred))
    return maes


def main():
    df = make_data()
    features = [c for c in df.columns if c not in ["date", "demand"]]

    fold_maes = walk_forward_cv(df, features)
    print("Walk-forward CV MAE per fold:", [round(m, 2) for m in fold_maes])
    print(f"Mean walk-forward MAE: {np.mean(fold_maes):.2f}")

    # Final holdout: last 90 days
    cut = len(df) - 90
    train, test = df.iloc[:cut], df.iloc[cut:]

    model_median = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=RANDOM_STATE)
    model_median.fit(train[features], train.demand)
    pred = model_median.predict(test[features])

    mae = mean_absolute_error(test.demand, pred)
    mape = mean_absolute_percentage_error(test.demand, pred)
    print(f"\nFinal holdout — MAE: {mae:.2f}   MAPE: {mape:.2%}")

    # Quantile models for a prediction interval
    model_lo = HistGradientBoostingRegressor(
        loss="quantile", quantile=0.1, max_iter=300, learning_rate=0.05, random_state=RANDOM_STATE
    )
    model_hi = HistGradientBoostingRegressor(
        loss="quantile", quantile=0.9, max_iter=300, learning_rate=0.05, random_state=RANDOM_STATE
    )
    model_lo.fit(train[features], train.demand)
    model_hi.fit(train[features], train.demand)
    pred_lo = model_lo.predict(test[features])
    pred_hi = model_hi.predict(test[features])

    coverage = np.mean((test.demand >= pred_lo) & (test.demand <= pred_hi))
    print(f"80% interval empirical coverage: {coverage:.1%}")

    plt.figure(figsize=(10, 5))
    plt.plot(test.date, test.demand, label="actual")
    plt.plot(test.date, pred, label="forecast (median)")
    plt.fill_between(test.date, pred_lo, pred_hi, alpha=0.2, label="80% interval")
    plt.legend()
    plt.title("Demand forecast with prediction interval")
    plt.tight_layout()
    plt.savefig("forecast.png")
    plt.close()

    joblib.dump({"median": model_median, "lo": model_lo, "hi": model_hi, "features": features}, "demand_model.joblib", compress=3)
    print("Saved: demand_model.joblib, forecast.png")


if __name__ == "__main__":
    main()
