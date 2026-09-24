# 18 - Fake Review Detection (Level 2)

NLP + metadata classification screening reviews as genuine or suspicious.

## What changed from Level 1
- The Level 1 fake class was trivially separable (ALL CAPS + "!!!" spam).
  This version generates harder, more realistic fake reviews that mimic
  genuine enthusiastic tone but reuse templated phrasing.
- Adds **reviewer-metadata features** — rating deviation from the product's
  average, and posting frequency in the last week — since real fake-review
  detection relies on this combination, not text alone.
- Compares a **text-only model against a text+metadata model** explicitly.
- Framed throughout as a **screening tool**, not a verdict — the demo
  app's output says so directly.

## Honest limitation
Still synthetic data (5 fake templates), so scores remain near-perfect.
The real next step is a labeled real-world dataset (Yelp/Amazon fake
review corpora), where text+metadata should show a much clearer lift over
text-only than it does here.

## Run
```bash
pip install -r requirements.txt
python train.py
python app.py
```

## Outputs
`fake_review_model.joblib`

## Level 3 ideas
Burst-detection (many similar reviews in a short time window); account-age
and verified-purchase features; ensemble of text + graph-based reviewer
network features.
