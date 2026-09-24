import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt, seaborn as sns

print("Iris Flower Classifier")
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, pred)*100:.2f}%")
print(classification_report(y_test, pred, target_names=iris.target_names))

# Predict your own
sample = [5.1, 3.5, 1.4, 0.2]
print(f"Sample {sample} -> {iris.target_names[model.predict([sample])[0]]}")

# Plot
df = pd.DataFrame(X, columns=iris.feature_names)
df['species'] = [iris.target_names[i] for i in y]
sns.pairplot(df, hue='species')
plt.savefig('pairplot.png')
print("Saved pairplot.png")
