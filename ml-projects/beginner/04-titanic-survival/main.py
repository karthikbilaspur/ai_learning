import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Titanic Survival Prediction - synthetic demo")

np.random.seed(42)
n=1000
df = pd.DataFrame({
    'Age': np.random.randint(1,70,n),
    'Fare': np.random.randint(10,500,n),
    'Sex': np.random.choice([0,1], n), # 0 male, 1 female
    'Pclass': np.random.choice([1,2,3], n)
})
# Simple rule: females and 1st class survive more
df['Survived'] = ((df['Sex']==1).astype(int) + (df['Pclass']==1).astype(int) + (df['Age']<10).astype(int) + np.random.randint(0,2,n) >=2).astype(int)

X = df[['Age','Fare','Sex','Pclass']]
y = df['Survived']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test))*100:.1f}%")
print("Feature importance:", dict(zip(X.columns, model.feature_importances_)))

# Predict example passenger
sample = pd.DataFrame([[25, 100, 1, 1]], columns=X.columns) # 25yr female 1st class
print(f"Sample passenger {sample.values[0]} -> Survived? {model.predict(sample)[0]} (1=yes, 0=no)")
