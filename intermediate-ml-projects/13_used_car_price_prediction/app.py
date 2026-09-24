"""Interactive demo for the used car price model.
Run: python train.py   (once, to produce used_car_price_model.joblib)
     python app.py
"""
import joblib
import pandas as pd
import gradio as gr

model = joblib.load("used_car_price_model.joblib")
spec = joblib.load("feature_spec.joblib")


def predict(brand, fueltype, aspiration, doornumber, carbody, drivewheel, enginelocation,
            enginetype, cylindernumber, fuelsystem, symboling, wheelbase, carlength,
            carwidth, carheight, curbweight, enginesize, boreratio, stroke,
            compressionratio, horsepower, peakrpm, citympg, highwaympg):
    row = pd.DataFrame([{
        "brand": brand, "fueltype": fueltype, "aspiration": aspiration, "doornumber": doornumber,
        "carbody": carbody, "drivewheel": drivewheel, "enginelocation": enginelocation,
        "enginetype": enginetype, "cylindernumber": cylindernumber, "fuelsystem": fuelsystem,
        "symboling": symboling, "wheelbase": wheelbase, "carlength": carlength,
        "carwidth": carwidth, "carheight": carheight, "curbweight": curbweight,
        "enginesize": enginesize, "boreratio": boreratio, "stroke": stroke,
        "compressionratio": compressionratio, "horsepower": horsepower, "peakrpm": peakrpm,
        "citympg": citympg, "highwaympg": highwaympg,
    }])
    price = model.predict(row)[0]
    return f"${price:,.0f}"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Textbox(value="toyota", label="Brand"),
        gr.Dropdown(["gas", "diesel"], value="gas", label="Fuel type"),
        gr.Dropdown(["std", "turbo"], value="std", label="Aspiration"),
        gr.Dropdown(["two", "four"], value="four", label="Doors"),
        gr.Dropdown(["sedan", "hatchback", "wagon", "hardtop", "convertible"], value="sedan", label="Body"),
        gr.Dropdown(["fwd", "rwd", "4wd"], value="fwd", label="Drive wheel"),
        gr.Dropdown(["front", "rear"], value="front", label="Engine location"),
        gr.Dropdown(["ohc", "ohcf", "ohcv", "dohc", "l", "rotor"], value="ohc", label="Engine type"),
        gr.Dropdown(["four", "six", "five", "three", "twelve", "two", "eight"], value="four", label="Cylinders"),
        gr.Dropdown(["mpfi", "2bbl", "idi", "1bbl", "spdi", "4bbl", "mfi", "spfi"], value="mpfi", label="Fuel system"),
        gr.Slider(-2, 3, value=0, step=1, label="Symboling (risk rating)"),
        gr.Slider(85, 130, value=98, label="Wheelbase"),
        gr.Slider(140, 210, value=175, label="Car length"),
        gr.Slider(60, 75, value=66, label="Car width"),
        gr.Slider(47, 60, value=54, label="Car height"),
        gr.Slider(1500, 4100, value=2500, label="Curb weight"),
        gr.Slider(60, 330, value=130, label="Engine size"),
        gr.Slider(2.5, 4.0, value=3.3, label="Bore ratio"),
        gr.Slider(2.0, 4.2, value=3.2, label="Stroke"),
        gr.Slider(7, 23, value=9, label="Compression ratio"),
        gr.Slider(48, 290, value=110, label="Horsepower"),
        gr.Slider(4150, 6600, value=5200, label="Peak RPM"),
        gr.Slider(10, 50, value=25, label="City MPG"),
        gr.Slider(15, 55, value=30, label="Highway MPG"),
    ],
    outputs=gr.Textbox(label="Predicted price"),
    title="Used Car Price Prediction — Level 2",
)

if __name__ == "__main__":
    demo.launch()
