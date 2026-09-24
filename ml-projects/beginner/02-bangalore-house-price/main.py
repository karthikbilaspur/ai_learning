import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

print("Bangalore House Price Prediction - with synthetic sample data")
# Synthetic data that mimics Bengaluru data
np.random.seed(42)
data = {
    'location': np.random.choice(['Whitefield','Indiranagar','Jayanagar','Koramangala','HSR Layout'], 500),
    'bhk': np.random.randint(1,5,500),
    'sqft': np.random.randint(600,3000,500),
}
df = pd.DataFrame(data)
# price = base + sqft*rate + bhk premium + location premium
loc_rate = {'Whitefield':40,'Indiranagar':120,'Jayanagar':90,'Koramangala':100,'HSR Layout':85}
df['price_lakhs'] = df['sqft']*0.05 + df['bhk']*10 + df['location'].map(loc_rate) + np.random.normal(0,10,500)

X = df[['location','bhk','sqft']]
y = df['price_lakhs']

preprocess = ColumnTransformer([('loc', OneHotEncoder(handle_unknown='ignore'), ['location'])], remainder='passthrough')
model = Pipeline([('pre', preprocess), ('reg', LinearRegression())])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
print(f"R2 Score: {model.score(X_test, y_test):.2f}")

def predict_price(location, bhk, sqft):
    price = model.predict(pd.DataFrame([[location,bhk,sqft]], columns=['location','bhk','sqft']))[0]
    print(f"{sqft} sqft, {bhk}BHK, {location} -> Rs {price:.1f} Lakhs")

# Test the example from prompt
predict_price('Whitefield', 2, 1200)
predict_price('Indiranagar', 3, 1800)

# Interactive
try:
    loc = input("Enter location [Whitefield/Indiranagar/Jayanagar/Koramangala/HSR Layout] (default Whitefield): ") or "Whitefield"
    bhk = int(input("Enter BHK (e.g. 2): ") or 2)
    sqft = int(input("Enter sqft (e.g. 1200): ") or 1200)
    predict_price(loc, bhk, sqft)
except:
    print("Interactive skipped")
