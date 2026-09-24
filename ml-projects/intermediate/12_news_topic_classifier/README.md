# 12 - News Topic Classifier (Level 2)

TF-IDF text classification across 5 topics, upgraded from a 10-sentence
repeated toy dataset.

## What changed from Level 1
- Much larger, templated corpus (~365 unique headlines from 25 sentence
  templates x vocabulary swaps) instead of the same 10 sentences repeated 20x.
- Compares **Logistic Regression, Linear SVM, and SGD** via 5-fold
  stratified cross-validation instead of one fixed model.
- Confusion matrix and per-class F1 reported, not just an overall report.
- Interactive Gradio demo (`app.py`).

## Honest limitation
This is still a templated/synthetic corpus, so accuracy is near-perfect
(too easy). The real Level 2+ step is swapping `load_data()` for a genuine
labeled corpus (AG News, BBC News, or 20 Newsgroups) — the rest of the
pipeline (CV comparison, confusion matrix, saved model) works unchanged
once you point it at real text.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`news_topic_model.joblib`, `confusion_matrix.png`

## Level 3 ideas
Swap TF-IDF for sentence embeddings or a fine-tuned DistilBERT; serve via
FastAPI; add an active-learning loop for low-confidence predictions.
