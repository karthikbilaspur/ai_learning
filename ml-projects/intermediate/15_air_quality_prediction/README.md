# 15 - Air Quality Prediction (Level 2)

Regression predicting an air-quality score from pollutant and weather features.

## What changed from Level 1
- Compares **Random Forest, Gradient Boosting, and XGBoost** via 5-fold CV
  instead of one fixed Random Forest.
- Hyperparameter tuning for the winning model.
- Residual diagnostics (residuals-vs-predicted + distribution) to check for
  systematic bias, not just a single MAE/R² number.
- **SHAP summary plot** for feature importance.
- Interactive Gradio demo (`app.py`).

## Results
Gradient Boosting won CV comparison; after tuning: **MAE ≈ 4.7, R² ≈ 0.968**
on the held-out test set.

## Honest limitation
Still synthetic, hourly-independent data (no real time-series structure).

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`air_quality_model.joblib`, `feature_order.joblib`, `residual_diagnostics.png`,
`shap_summary.png`

## Level 3 ideas
Real hourly data (UCI Air Quality dataset or a live OpenAQ/CPCB API pull)
reshaped into a genuine time-series problem with lag features; compare
tree models against Prophet/LSTM.
