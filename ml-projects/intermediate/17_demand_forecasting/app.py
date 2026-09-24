"""Interactive demo for the demand forecasting model.
Run: python train.py   (once, to produce demand_model.joblib)
     python app.py

Since this is a lag-feature model, the demo lets you enter recent history
directly (as if you were forecasting tomorrow from the last few weeks).
"""
import joblib
import pandas as pd
import gradio as gr

bundle = joblib.load("demand_model.joblib")
median, lo, hi, features = bundle["median"], bundle["lo"], bundle["hi"], bundle["features"]


def predict(lag_1, lag_7, lag_14, lag_28, rolling_7, rolling_28,
            dayofweek, month, is_holiday, is_promo):
    row = pd.DataFrame([{
        "is_holiday": int(is_holiday), "is_promo": int(is_promo),
        "lag_1": lag_1, "lag_7": lag_7, "lag_14": lag_14, "lag_28": lag_28,
        "rolling_7": rolling_7, "rolling_28": rolling_28,
        "dayofweek": dayofweek, "month": month,
    }])[features]
    p_lo = lo.predict(row)[0]
    p_med = median.predict(row)[0]
    p_hi = hi.predict(row)[0]
    return f"Forecast: {p_med:.0f} units\n80% interval: {p_lo:.0f} – {p_hi:.0f} units"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Slider(50, 200, value=110, label="Demand 1 day ago"),
        gr.Slider(50, 200, value=110, label="Demand 7 days ago"),
        gr.Slider(50, 200, value=108, label="Demand 14 days ago"),
        gr.Slider(50, 200, value=105, label="Demand 28 days ago"),
        gr.Slider(50, 200, value=110, label="7-day rolling average"),
        gr.Slider(50, 200, value=108, label="28-day rolling average"),
        gr.Slider(0, 6, value=2, step=1, label="Day of week (0=Mon)"),
        gr.Slider(1, 12, value=6, step=1, label="Month"),
        gr.Checkbox(label="Is holiday"),
        gr.Checkbox(label="Is promotion running"),
    ],
    outputs=gr.Textbox(label="Forecast"),
    title="Retail Demand Forecasting — Level 2",
)

if __name__ == "__main__":
    demo.launch()
