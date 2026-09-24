from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

print("Handwritten Digit Recognition (using sklearn digits - 8x8, works like MNIST)")

digits = load_digits()
X, y = digits.data, digits.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, pred)*100:.2f}%")

# Show some predictions
for i in range(5):
    plt.matshow(digits.images[y_test.tolist().index(y_test[i])] if False else digits.images[i].reshape(8,8))
    # Actually show first 5 test samples
plt.figure(figsize=(10,3))
for i in range(5):
    plt.subplot(1,5,i+1)
    plt.imshow(X_test[i].reshape(8,8), cmap='gray')
    plt.title(f"Pred: {model.predict([X_test[i]])[0]}")
    plt.axis('off')
plt.savefig('predictions.png')
print("Saved predictions.png - 5 sample digits with predictions")

# To upgrade to full MNIST + CNN:
# pip install tensorflow
# from tensorflow.keras.datasets import mnist
# (X_train, y_train), (X_test, y_test) = mnist.load_data()
