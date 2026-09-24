from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Movie Review Sentiment Analysis")

reviews = [
    ("I loved this movie, it was fantastic and amazing", "positive"),
    ("This movie was boring and terrible", "negative"),
    ("Great acting, wonderful story", "positive"),
    ("Worst film ever, waste of time", "negative"),
    ("An excellent masterpiece", "positive"),
    ("I hated it, very bad", "negative"),
    ("Beautiful cinematography and great direction", "positive"),
    ("Not good, disappointing", "negative"),
] * 25

texts, labels = zip(*reviews)
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

vec = TfidfVectorizer()
X_train_vec = vec.fit_transform(X_train)

model = LogisticRegression()
model.fit(X_train_vec, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(vec.transform(X_test)))*100:.1f}%")

def sentiment(text):
    pred = model.predict(vec.transform([text]))[0]
    print(f"'{text}' -> {pred}")

sentiment("This movie was boring")
sentiment("I absolutely loved it!")
sentiment("It was okay but not great")

try:
    user = input("Enter a review to test: ")
    if user.strip():
        sentiment(user)
except:
    pass
