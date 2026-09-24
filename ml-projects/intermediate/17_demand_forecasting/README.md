# 17 - Retail Demand Forecasting (Level 2)

Time-series regression forecasting daily product demand.

## What changed from Level 1
- Added **holiday and promotion flags** as calendar features (missing
  from Level 1's trend+seasonality-only synthetic series).
- **Walk-forward (rolling-origin) cross-validation** — the statistically
  correct way to validate a time-series model — instead of one fixed split.
- Reports **MAPE** alongside MAE.
- **Quantile regression** (10th/90th percentile models) gives an 80%
  prediction interval, not just a point forecast.
- Interactive Gradio demo (`app.py`) for a single what-if forecast.

## Results
Walk-forward mean MAE ≈ 6.6; final holdout MAE ≈ 5.9 (MAPE ≈ 4.1%).

## Honest limitation
The 80% interval's empirical coverage came out around 52% rather than 80%
in testing — the quantile models need more tuning (more iterations /
different loss settings) before the interval width can be trusted. Treat
the interval as illustrative, not calibrated, until that's fixed.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`demand_model.joblib`, `forecast.png`

## Level 3 ideas
Real retail dataset (M5/Rossmann/Walmart) with per-store, per-SKU series
and hierarchical reconciliation; compare against Prophet/SARIMA.
