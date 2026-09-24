"""Interactive demo for the employee attrition model.
Run: python train.py   (once, to produce attrition_model.joblib)
     python app.py
"""
import joblib
import pandas as pd
import gradio as gr

model = joblib.load("attrition_model.joblib")


def predict(age, monthly_income, years_at_company, job_satisfaction, overtime,
            distance_from_home, department, business_travel, work_life_balance):
    row = pd.DataFrame([{
        "Age": age, "DailyRate": 800, "Department": department,
        "DistanceFromHome": distance_from_home, "Education": 3, "EducationField": "Life Sciences",
        "EnvironmentSatisfaction": 3, "Gender": "Male", "HourlyRate": 65,
        "JobInvolvement": 3, "JobLevel": 2, "JobRole": "Sales Executive",
        "JobSatisfaction": job_satisfaction, "MaritalStatus": "Married",
        "MonthlyIncome": monthly_income, "MonthlyRate": 15000, "NumCompaniesWorked": 2,
        "OverTime": overtime, "PercentSalaryHike": 13, "PerformanceRating": 3,
        "RelationshipSatisfaction": 3, "StockOptionLevel": 1,
        "TotalWorkingYears": years_at_company + 2, "TrainingTimesLastYear": 2,
        "WorkLifeBalance": work_life_balance, "YearsAtCompany": years_at_company,
        "YearsInCurrentRole": min(years_at_company, 4), "YearsSinceLastPromotion": 1,
        "YearsWithCurrManager": min(years_at_company, 3), "BusinessTravel": business_travel,
    }])
    prob = model.predict_proba(row)[0, 1]
    verdict = "⚠️ Elevated attrition risk" if prob >= 0.3 else "✅ Low attrition risk"
    return f"{verdict}\nEstimated probability of leaving: {prob:.1%}"


demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Slider(18, 60, value=30, label="Age"),
        gr.Slider(1000, 20000, value=5000, label="Monthly income ($)"),
        gr.Slider(0, 20, value=3, label="Years at company"),
        gr.Slider(1, 4, value=3, step=1, label="Job satisfaction (1-4)"),
        gr.Dropdown(["Yes", "No"], value="No", label="Works overtime"),
        gr.Slider(0, 30, value=5, label="Distance from home"),
        gr.Dropdown(["Sales", "Research & Development", "Human Resources"], value="Sales", label="Department"),
        gr.Dropdown(["Travel_Rarely", "Travel_Frequently", "Non-Travel"], value="Travel_Rarely", label="Business travel"),
        gr.Slider(1, 4, value=3, step=1, label="Work-life balance (1-4)"),
    ],
    outputs=gr.Textbox(label="Prediction"),
    title="Employee Attrition Prediction — Level 2",
)

if __name__ == "__main__":
    demo.launch()
