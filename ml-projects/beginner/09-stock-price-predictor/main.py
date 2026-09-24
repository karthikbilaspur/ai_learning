import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

print("Stock Price Trend Predictor (Synthetic demo + yfinance support)")

# Synthetic stock data - always works offline
np.random.seed(42)
days = 200
price = 100 + np.cumsum(np.random.randn(days)*0.5 + 0.1)

df = pd.DataFrame({'Close': price})
df['Day'] = range(len(df))

# Use last 5 days as features to predict next day (simple time series)
X, y = [], []
for i in range(5, len(df)):
    X.append(df['Close'].iloc[i-5:i].values)
    y.append(df['Close'].iloc[i])
X, y = np.array(X), np.array(y)

split = int(len(X)*0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

model = LinearRegression()
model.fit(X_train, y_train)
pred = model.predict(X_test)

print(f"Test on last {len(y_test)} days")
plt.figure()
plt.plot(y_test, label='Actual')
plt.plot(pred, label='Predicted')
plt.legend()
plt.title('Stock Price: Actual vs Predicted')
plt.savefig('stock_prediction.png')
print("Saved stock_prediction.png")

# Try live data if yfinance is installed
try:
    import yfinance as yf
    print("\nTrying live TCS.NS data with yfinance...")
    data = yf.download("TCS.NS", period="6mo", interval="1d", progress=False)
    if not data.empty:
        print(f"Downloaded {len(data)} live rows")
        data['Day'] = range(len(data))
        # Quick plot of live close
        plt.figure()
        data['Close'].plot()
        plt.title('TCS.NS Last 6 Months (Live)')
        plt.savefig('tcs_live.png')
        print("Saved tcs_live.png with live data")
    else:
        print("yfinance returned empty, using synthetic only")
except Exception as e:
    print(f"yfinance not installed or offline ({e}). Synthetic demo still successful.")

print("\nNote: Simple Linear Regression for learning only, not for real trading!")
