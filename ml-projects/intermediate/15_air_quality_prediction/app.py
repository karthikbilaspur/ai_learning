"""Interactive demo for the air quality model.
Run: python train.py   (once, to produce air_quality_model.joblib)
     python app.py
"""
import joblib
import pandas as pd
import gradio as gr

model = joblib.load("air_quality_model.joblib")
feature_order = joblib.load("feature_order.joblib")


def predict(pm25, pm10, no2, so2, co, temperature, humidity, wind_speed):
    row = pd.DataFrame([{
        "pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co,
        "temperature": temperature, "humidity": humidity, "wind_speed": wind_speed,
    }])[feature_order]
    score = model.predict(row)[0]
    return f"{score:.1f} / 100"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Slider(0, 150, value=30, label="PM2.5"),
        gr.Slider(0, 250, value=60, label="PM10"),
        gr.Slider(0, 100, value=25, label="NO2"),
        gr.Slider(0, 60, value=12, label="SO2"),
        gr.Slider(0, 8, value=1.2, label="CO"),
        gr.Slider(-5, 45, value=27, label="Temperature (°C)"),
        gr.Slider(10, 100, value=55, label="Humidity (%)"),
        gr.Slider(0, 15, value=3, label="Wind speed"),
    ],
    outputs=gr.Textbox(label="Predicted air quality score (higher = cleaner)"),
    title="Air Quality Prediction — Level 2",
)

if __name__ == "__main__":
    demo.launch()
