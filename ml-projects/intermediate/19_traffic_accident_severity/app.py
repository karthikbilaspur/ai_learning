"""Interactive demo for the traffic accident severity model.
Run: python train.py   (once, to produce severity_model.joblib)
     python app.py
"""
import joblib
import pandas as pd
import gradio as gr

bundle = joblib.load("severity_model.joblib")
rf, features = bundle["rf"], bundle["features"]


def predict(speed_limit, rain_mm, visibility_km, traffic_density, night, road_risk_score, is_weekend):
    row = pd.DataFrame([{
        "speed_limit": speed_limit, "rain_mm": rain_mm, "visibility_km": visibility_km,
        "traffic_density": traffic_density, "night": int(night),
        "road_risk_score": road_risk_score, "is_weekend": int(is_weekend),
    }])[features]
    pred = rf.predict(row)[0]
    probs = dict(zip(rf.classes_, rf.predict_proba(row)[0]))
    breakdown = "\n".join(f"{k}: {v:.2f}" for k, v in probs.items())
    return f"Predicted severity: {pred}\n\n{breakdown}"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Dropdown([30, 40, 50, 60, 80, 100], value=50, label="Speed limit"),
        gr.Slider(0, 20, value=1, label="Rainfall (mm)"),
        gr.Slider(0.5, 15, value=8, label="Visibility (km)"),
        gr.Slider(0, 1, value=0.4, label="Traffic density"),
        gr.Checkbox(label="Night time"),
        gr.Slider(0, 1, value=0.2, label="Road segment risk score"),
        gr.Checkbox(label="Weekend"),
    ],
    outputs=gr.Textbox(label="Prediction"),
    title="Traffic Accident Severity — Level 2",
)

if __name__ == "__main__":
    demo.launch()
