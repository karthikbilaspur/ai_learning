# 13 - Used Car Price Prediction (Level 2)

Regression on the real **CarPrice_Assignment** dataset (205 US-market cars),
upgraded from a synthetic-data demo.

## What changed from Level 1
- Real dataset (`data/CarPrice_Assignment.csv`) with brand extracted and
  cleaned from `CarName` (fixes typos like "maxda" -> "mazda").
- Compares **Random Forest, Gradient Boosting, and XGBoost** via 5-fold CV.
- Hyperparameter tuning (`RandomizedSearchCV`) for the winning model.
- **SHAP summary plot** explaining which features drive each prediction.
- Interactive Gradio demo (`app.py`) — enter spec, get a price estimate.

## Results
Random Forest won CV comparison; after tuning: **MAE ≈ $1,331, R² ≈ 0.955**
on the held-out test set.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`used_car_price_model.joblib`, `feature_spec.joblib`, `shap_summary.png`

## Level 3 ideas
Larger real-world dataset (tens of thousands of listings); per-prediction
SHAP waterfall in the demo app; deploy as a public web form.
