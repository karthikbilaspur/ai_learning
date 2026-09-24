"""Interactive demo for the fake-review screening model.
Run: python train.py   (once, to produce fake_review_model.joblib)
     python app.py
"""
import joblib
import scipy.sparse as sp
import gradio as gr

bundle = joblib.load("fake_review_model.joblib")
tfidf, model, meta_cols = bundle["tfidf"], bundle["model"], bundle["meta_cols"]


def check(review_text, rating, product_avg_rating, reviews_last_week):
    deviation = rating - product_avg_rating
    Xtext = tfidf.transform([review_text])
    Xmeta = sp.csr_matrix([[rating, deviation, reviews_last_week]])
    X = sp.hstack([Xtext, Xmeta])
    prob = model.predict_proba(X)[0, 1]
    verdict = "⚠️ Flagged for review" if prob >= 0.5 else "✅ Looks genuine"
    return f"{verdict}\nSuspicion score: {prob:.2f}\n(screening signal only — not proof)"


demo = gr.Interface(
    fn=check,
    inputs=[
        gr.Textbox(lines=3, label="Review text"),
        gr.Slider(1, 5, value=5, step=0.5, label="Star rating given"),
        gr.Slider(1, 5, value=4, step=0.1, label="Product's average rating"),
        gr.Slider(0, 15, value=0, step=1, label="Reviews by this author in the last week"),
    ],
    outputs=gr.Textbox(label="Result"),
    title="Fake Review Detection — Level 2",
    description="A screening tool, not proof — treat flagged reviews as candidates for manual review.",
)

if __name__ == "__main__":
    demo.launch()
