"""Interactive demo for the news topic classifier.
Run: python train.py   (once, to produce news_topic_model.joblib)
     python app.py
"""
import joblib
import gradio as gr

model = joblib.load("news_topic_model.joblib")


def classify(headline):
    if not headline.strip():
        return "Type a headline first."
    pred = model.predict([headline])[0]
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([headline])[0]
        ranked = sorted(zip(model.classes_, probs), key=lambda x: -x[1])
        breakdown = "\n".join(f"{c}: {p:.2f}" for c, p in ranked)
        return f"Predicted topic: {pred}\n\n{breakdown}"
    return f"Predicted topic: {pred}"


demo = gr.Interface(
    fn=classify,
    inputs=gr.Textbox(lines=2, label="News headline / snippet"),
    outputs=gr.Textbox(label="Prediction"),
    title="News Topic Classifier — Level 2",
    examples=[
        "The central bank raised interest rates unexpectedly.",
        "The striker scored two goals in the final match.",
        "Researchers published findings about climate change.",
    ],
)

if __name__ == "__main__":
    demo.launch()
