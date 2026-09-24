# 27 Retrieval Time Series -- Level 1

Retrieval-Augmented Time Series Forecasting.

## What's here
- `src/make_data.py` - generates a synthetic seasonal+trend+noise series
  (none was included)
- `src/retriever.py` - `retrieve()` now supports `exclude_idx` so a
  query window can be excluded from its own retrieval corpus (previously
  a training window could trivially retrieve *itself* as the top match)
- `src/train.py` - chronological train/test split (was none), retrieval
  corpus built from the training split only, reports held-out MAE/MSE
  (was training loss only), checkpoints the model

## Run
```bash
pip install -r ../requirements.txt
python src/make_data.py --length 5000
python src/train.py --series_path data/series.npy --epochs 30
```
