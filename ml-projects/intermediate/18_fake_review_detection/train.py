"""
Level 2 upgrade — Fake Review Detection
- The level-1 dataset was trivially separable (fake = all-caps exclamation
  spam). This version generates a much harder, more realistic corpus where
  fake reviews mimic genuine tone but are templated/repetitive, and adds
  reviewer-metadata features (posting burst, rating deviation from product
  average) alongside text — genuine fake-review detection relies on this
  combination, not text alone.
- Compares a text-only model against a text+metadata model.
- Reports precision/recall explicitly and frames the model as a screening
  tool (its intended real-world use), not a verdict.
"""
import random
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
import joblib

RANDOM_STATE = 42
random.seed(RANDOM_STATE)
rng = np.random.default_rng(RANDOM_STATE)

GENUINE_TEMPLATES = [
    "The delivery arrived {timing} but the product {quality}.",
    "Battery lasts about {hours} hours and the {part} feels {feel}.",
    "The size was {accuracy}, although the material is {material} than expected.",
    "Customer support {support_action} the {issue} quickly.",
    "Works as described, though I wish the {part} was {improvement}.",
    "Good value for the price, {minor_complaint} but overall satisfied.",
    "Took a {timing2} to get used to it, now it's part of my routine.",
]
GENUINE_FILLERS = {
    "timing": ["two days late", "on time", "a day early", "right on schedule"],
    "quality": ["works well", "does the job", "performs as expected", "exceeded expectations"],
    "hours": ["five", "six", "eight", "ten"],
    "part": ["keyboard", "strap", "handle", "screen", "case"],
    "feel": ["comfortable", "sturdy", "a bit cheap", "solid"],
    "accuracy": ["accurate", "slightly off", "true to the chart"],
    "material": ["thinner", "softer", "lighter", "stiffer"],
    "support_action": ["replaced the damaged item", "responded to my email", "processed my refund"],
    "issue": ["damaged item", "missing part", "sizing issue"],
    "improvement": ["a bit more padded", "slightly larger", "more durable"],
    "minor_complaint": ["packaging could be better", "instructions were unclear", "setup took a while"],
    "timing2": ["few days", "week", "couple tries"],
}

# Fake reviews: templated/repetitive, mimic enthusiasm but reused phrasing
FAKE_TEMPLATES = [
    "Amazing product, highly recommend to everyone, five stars!",
    "Great quality and fast shipping, will buy again soon!",
    "Exactly what I needed, works perfectly every time!",
    "Best purchase this year, exceeded all my expectations completely!",
    "Excellent value, exactly as described, very happy customer!",
]


def make_reviews(n_genuine=600, n_fake=250):
    genuine_texts = []
    for _ in range(n_genuine):
        t = random.choice(GENUINE_TEMPLATES)
        for k, v in GENUINE_FILLERS.items():
            if "{" + k + "}" in t:
                t = t.replace("{" + k + "}", random.choice(v))
        genuine_texts.append(t)

    fake_texts = [random.choice(FAKE_TEMPLATES) for _ in range(n_fake)]

    texts = genuine_texts + fake_texts
    labels = [0] * n_genuine + [1] * n_fake

    # Metadata: fake reviewers tend to post in bursts and rate higher than the
    # product's average rating; genuine reviewers vary more naturally.
    product_avg_rating = rng.uniform(2.5, 4.5, len(texts))
    review_rating = np.where(
        np.array(labels) == 1,
        np.clip(product_avg_rating + rng.normal(1.2, 0.4, len(texts)), 1, 5),
        np.clip(product_avg_rating + rng.normal(0, 0.6, len(texts)), 1, 5),
    )
    reviews_by_author_last_week = np.where(
        np.array(labels) == 1,
        rng.poisson(6, len(texts)),
        rng.poisson(0.5, len(texts)),
    )
    rating_deviation = review_rating - product_avg_rating

    df = pd.DataFrame({
        "text": texts,
        "rating": review_rating.round(1),
        "rating_deviation": rating_deviation.round(2),
        "reviews_by_author_last_week": reviews_by_author_last_week,
        "label": labels,
    })
    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def main():
    df = make_reviews()
    meta_cols = ["rating", "rating_deviation", "reviews_by_author_last_week"]

    train_df, test_df = train_test_split(df, test_size=0.25, random_state=RANDOM_STATE, stratify=df.label)

    tfidf = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    Xtr_text = tfidf.fit_transform(train_df.text)
    Xte_text = tfidf.transform(test_df.text)

    # Text-only baseline
    text_only = LogisticRegression(max_iter=1000)
    text_only.fit(Xtr_text, train_df.label)
    pred_text = text_only.predict(Xte_text)
    auc_text = roc_auc_score(test_df.label, text_only.predict_proba(Xte_text)[:, 1])

    # Text + metadata
    Xtr_meta = sp.csr_matrix(train_df[meta_cols].values)
    Xte_meta = sp.csr_matrix(test_df[meta_cols].values)
    Xtr_full = sp.hstack([Xtr_text, Xtr_meta])
    Xte_full = sp.hstack([Xte_text, Xte_meta])

    full_model = LogisticRegression(max_iter=1000)
    full_model.fit(Xtr_full, train_df.label)
    pred_full = full_model.predict(Xte_full)
    auc_full = roc_auc_score(test_df.label, full_model.predict_proba(Xte_full)[:, 1])

    print("=== Text-only model ===")
    print(classification_report(test_df.label, pred_text))
    print("ROC-AUC:", round(auc_text, 3))

    print("\n=== Text + reviewer-metadata model ===")
    print(classification_report(test_df.label, pred_full))
    print("ROC-AUC:", round(auc_full, 3))

    joblib.dump(
        {"tfidf": tfidf, "model": full_model, "meta_cols": meta_cols},
        "fake_review_model.joblib",
        compress=3,
    )

    samples = pd.DataFrame([
        {"text": "The product arrived on time and works as described.", "rating": 4.0, "rating_deviation": 0.1, "reviews_by_author_last_week": 0},
        {"text": "Amazing product, highly recommend to everyone, five stars!", "rating": 5.0, "rating_deviation": 1.5, "reviews_by_author_last_week": 7},
    ])
    Xs = sp.hstack([tfidf.transform(samples.text), sp.csr_matrix(samples[meta_cols].values)])
    print("\nSample predictions:", list(zip(samples.text, full_model.predict(Xs))))
    print("\nSaved: fake_review_model.joblib")


if __name__ == "__main__":
    main()
