# 16 - Employee Attrition Prediction (Level 2)

Binary classification on the real **IBM HR Analytics Attrition** dataset
(1,470 employees, ~16% attrition rate).

## What changed from Level 1
- Real dataset (`data/hr_attrition.csv`) instead of synthetic data.
- Explicit class-imbalance handling (`class_weight="balanced"` /
  `scale_pos_weight`) with **PR-AUC** as the primary CV metric, since
  accuracy is misleading on an imbalanced target.
- Compares **Logistic Regression, Random Forest, and XGBoost**.
- **SHAP summary plot** for individual-level interpretation — "why is this
  employee flagged" matters more to an HR audience than raw accuracy.
- Interactive Gradio demo (`app.py`).

## Results
XGBoost won CV comparison. On the held-out test set: **ROC-AUC ≈ 0.78,
PR-AUC ≈ 0.50** — realistic numbers for real, noisy HR data (a big drop
from the Level 1 synthetic version's inflated scores, which is expected
and worth calling out in a portfolio write-up).

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`attrition_model.joblib`, `precision_recall.png`, `shap_summary.png`

## Level 3 ideas
Calibrate predicted probabilities; build a small HR-facing dashboard to
explore risk by department; fairness audit across gender/age groups.
