"""Interactive demo for the anomaly detector.
Run: python train.py   (once, to produce anomaly_model.joblib)
     python app.py
"""
import joblib
import gradio as gr

bundle = joblib.load("anomaly_model.joblib")
scaler, model, features, threshold = bundle["scaler"], bundle["model"], bundle["features"], bundle["threshold"]


def check(amount, hour, distance_km, merchant_risk, txns_last_hour):
    X = scaler.transform([[amount, hour, distance_km, merchant_risk, txns_last_hour]])
    score = float(-model.score_samples(X)[0])
    flagged = score >= threshold
    verdict = "⚠️ FLAGGED as suspicious" if flagged else "✅ Looks normal"
    return f"{verdict}\nAnomaly score: {score:.3f} (flag threshold: {threshold:.3f})"


demo = gr.Interface(
    fn=check,
    inputs=[
        gr.Slider(1, 6000, value=80, label="Amount ($)"),
        gr.Slider(0, 23, value=14, step=1, label="Hour of day"),
        gr.Slider(0, 900, value=3, label="Distance from home (km)"),
        gr.Slider(0, 1, value=0.15, label="Merchant risk score (0=low, 1=high)"),
        gr.Slider(0, 15, value=1, step=1, label="Transactions in the last hour"),
    ],
    outputs=gr.Textbox(label="Result"),
    title="Credit Card Spending Anomaly Detector — Level 2",
)

if __name__ == "__main__":
    demo.launch()
