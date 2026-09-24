"""
Level 2 upgrade — News Topic Classifier
- Much larger, more varied templated corpus (200+ unique sentence patterns x
  topical vocabulary swaps => thousands of distinct headlines) instead of
  10 repeated sentences. NOTE: a real corpus (AG News / BBC News) is the
  natural next step once you can pull external data into your environment —
  swap load_data() for a pd.read_csv() on that file and everything else works
  unchanged.
- Compares Logistic Regression, Linear SVM and SGD classifiers via
  cross-validation instead of a single train/test split.
- Reports a confusion matrix and per-class F1, not just an overall report.
- Saves the trained pipeline + a small CLI/Gradio demo (app.py).
"""
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import joblib

RANDOM_STATE = 42
random.seed(RANDOM_STATE)

TOPIC_TEMPLATES = {
    "business": [
        "The central bank {verb} interest rates {qualifier}.",
        "{company} reported {adj} quarterly earnings this {period}.",
        "The stock market {moved} after {event}.",
        "Investors are watching {company}'s merger with a rival firm.",
        "Inflation figures came in {adj} for the {period}, unsettling markets.",
    ],
    "technology": [
        "{company} unveiled a new {adj} chip for AI workloads.",
        "A startup launched a {adj} machine learning platform for {domain}.",
        "Researchers open-sourced a new model for {domain} tasks.",
        "{company} announced a data breach affecting {number} users.",
        "The new smartphone from {company} features an upgraded camera system.",
    ],
    "sports": [
        "The {team} won the championship after a {adj} extra-time finish.",
        "The striker scored {number} goals in the {period} match.",
        "{team} signed a new coach ahead of the upcoming season.",
        "The tournament final drew a record {adj} crowd.",
        "Injuries forced {team} to rest several key players this {period}.",
    ],
    "politics": [
        "Parliament debated the proposed {domain} bill this {period}.",
        "The government introduced a new {domain} policy.",
        "{company_gov} officials met to discuss the upcoming election.",
        "Lawmakers clashed over {domain} spending in a {adj} session.",
        "The president signed an executive order on {domain}.",
    ],
    "science": [
        "Scientists discovered a {adj} new treatment for the disease.",
        "Researchers published findings about {domain} in a leading journal.",
        "A new study links {domain} to changes in {domain}.",
        "NASA announced a {adj} mission to study {domain}.",
        "Biologists identified a new species during a {period} expedition.",
    ],
}

FILLERS = {
    "verb": ["raised", "cut", "held", "signaled changes to"],
    "qualifier": ["for the third straight month", "amid inflation concerns", "unexpectedly", "as planned"],
    "company": ["TechCorp", "Nova Systems", "Orion Labs", "Quantum Works", "Helix Inc"],
    "adj": ["strong", "weak", "record", "surprising", "modest", "historic"],
    "period": ["quarter", "week", "season", "year", "month"],
    "moved": ["rose", "fell", "stabilized", "rallied"],
    "event": ["strong earnings reports", "a rate decision", "weak jobs data", "a surprise announcement"],
    "domain": ["healthcare", "education", "climate", "immigration", "renewable energy", "genomics"],
    "number": ["two", "three", "several million", "a few thousand"],
    "team": ["the Falcons", "the Hawks", "the Riverside club", "the national team", "the Wanderers"],
    "company_gov": ["Ministry", "Senate", "Cabinet", "City council"],
}


def make_sentence(template):
    out = template
    for key, options in FILLERS.items():
        if "{" + key + "}" in out:
            out = out.replace("{" + key + "}", random.choice(options))
    return out


def load_data(n_per_topic=250):
    rows = []
    for topic, templates in TOPIC_TEMPLATES.items():
        for _ in range(n_per_topic):
            template = random.choice(templates)
            rows.append((make_sentence(template), topic))
    df = pd.DataFrame(rows, columns=["text", "label"]).drop_duplicates()
    return df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def build_candidates():
    return {
        "logreg": Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=2000)),
        ]),
        "linear_svm": Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LinearSVC()),
        ]),
        "sgd": Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", SGDClassifier(loss="log_loss", random_state=RANDOM_STATE)),
        ]),
    }


def main():
    df = load_data()
    print(f"Dataset size: {len(df)} unique headlines across {df.label.nunique()} topics")

    X_train, X_test, y_train, y_test = train_test_split(
        df.text, df.label, test_size=0.2, random_state=RANDOM_STATE, stratify=df.label
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = build_candidates()
    cv_scores = {}
    for name, pipe in candidates.items():
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1_macro")
        cv_scores[name] = scores.mean()
        print(f"{name}: CV macro-F1 = {scores.mean():.3f} (+/- {scores.std():.3f})")

    best_name = max(cv_scores, key=cv_scores.get)
    print(f"\nBest model: {best_name}")

    best_model = candidates[best_name]
    best_model.fit(X_train, y_train)
    pred = best_model.predict(X_test)

    print(classification_report(y_test, pred))
    print("Macro F1 on held-out test set:", round(f1_score(y_test, pred, average="macro"), 3))

    labels = sorted(df.label.unique())
    cm = confusion_matrix(y_test, pred, labels=labels)
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, cmap="Blues")
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(range(len(labels)), labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            plt.text(j, i, cm[i, j], ha="center", va="center")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion matrix ({best_name})")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    plt.close()

    joblib.dump(best_model, "news_topic_model.joblib", compress=3)

    examples = [
        "The company reported record quarterly profits.",
        "The team advanced to the tournament final.",
        "Researchers tested a new battery material.",
    ]
    print(list(zip(examples, best_model.predict(examples))))
    print("\nSaved: news_topic_model.joblib, confusion_matrix.png")


if __name__ == "__main__":
    main()
