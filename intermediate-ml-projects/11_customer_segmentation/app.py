"""Interactive demo: predict which customer segment a new shopper falls into.
Run: python train.py   (once, to produce segmentation_model.joblib)
     python app.py      (to launch the demo)
"""
import json
import joblib
import gradio as gr

bundle = joblib.load("segmentation_model.joblib")
scaler, model, features = bundle["scaler"], bundle["model"], bundle["features"]

try:
    with open("cluster_names.json") as f:
        cluster_names = {int(k): v for k, v in json.load(f).items()}
except FileNotFoundError:
    cluster_names = {}


def predict(age, income, spending_score):
    X = scaler.transform([[age, income, spending_score]])
    cluster = int(model.predict(X)[0])
    label = cluster_names.get(cluster, f"Cluster {cluster}")
    return f"Cluster {cluster}  —  {label}"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Slider(15, 75, value=30, label="Age"),
        gr.Slider(10, 140, value=60, label="Annual Income (k$)"),
        gr.Slider(1, 100, value=50, label="Spending Score (1-100)"),
    ],
    outputs=gr.Textbox(label="Predicted segment"),
    title="Customer Segmentation — Level 2",
    description="Enter a customer's profile to see which behavioral segment they belong to.",
)

if __name__ == "__main__":
    demo.launch()
