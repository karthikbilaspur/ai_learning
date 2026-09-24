# 19 - Traffic Accident Severity Prediction (Level 2)

Multi-class classification predicting accident severity (low/medium/high).

## What changed from Level 1
- Severity is **ordered**, so alongside the plain multi-class Random Forest
  this adds an **ordinal classifier** (K-1 cumulative "is severity >= k"
  binary models) and compares them directly — plain multi-class accuracy
  treats "high predicted as low" the same as "high predicted as medium",
  which is the wrong cost structure for this problem.
- Reports the specific error that matters most: **P(predict "low" | actual
  "high")** for each model.
- Added a simulated road-segment risk feature (stand-in for a real
  geographic hotspot feature) and a night×weekend interaction.
- Interactive Gradio demo (`app.py`).

## Results
Random Forest: macro F1 ≈ 0.65, P(high→low) ≈ 5.1%.
Ordinal model: macro F1 ≈ 0.49, P(high→low) ≈ 11.5% — worse here, a useful
reminder that "respects the ordering" doesn't automatically mean "better
in practice"; the plain classifier actually made the costly mistake less often
on this synthetic data.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`severity_model.joblib`, `confusion_matrix.png`

## Level 3 ideas
Real dataset (US Accidents / UK STATS19) with genuine geographic features;
cost-sensitive loss that directly penalizes high-severity misses.
