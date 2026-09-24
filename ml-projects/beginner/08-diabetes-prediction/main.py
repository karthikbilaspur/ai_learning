import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

print("Diabetes Prediction")

# Synthetic Pima-like data
np.random.seed(42)
n=800
df = pd.DataFrame({
    'Pregnancies': np.random.randint(0,10,n),
    'Glucose': np.random.randint(80,200,n),
    'BloodPressure': np.random.randint(60,100,n),
    'BMI': np.random.uniform(18,45,n),
    'Age': np.random.randint(21,80,n),
})
df['Outcome'] = ((df['Glucose']>140).astype(int) + (df['BMI']>30).astype(int) + (df['Age']>45).astype(int) >=2).astype(int)
# Add noise
df['Outcome'] = df['Outcome'] ^ np.random.choice([0,1], n, p=[0.85,0.15])

X = df.drop('Outcome', axis=1)
y = df['Outcome']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test))*100:.1f}%")

def predict(preg, glu, bp, bmi, age):
    sample = scaler.transform([[preg, glu, bp, bmi, age]])
    pred = model.predict(sample)[0]
    print(f"Input Glucose={glu}, BMI={bmi:.1f}, Age={age} -> Diabetes: {'YES' if pred==1 else 'NO'}")

predict(2, 150, 80, 32.5, 50)
predict(0, 90, 70, 22.0, 25)
