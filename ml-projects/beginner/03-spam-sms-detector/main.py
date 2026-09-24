from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Spam SMS Detector")

# Small in-built dataset - works offline, no Kaggle needed
messages = [
    ("Free entry in 2 a wkly comp to win FA Cup final", "spam"),
    ("U dun say so early hor... U c already then say...", "ham"),
    ("WINNER!! As a valued network customer you have been selected", "spam"),
    ("Hey, are we still meeting for coffee tomorrow?", "ham"),
    ("Congratulations you won lottery! Call now", "spam"),
    ("I'll be late, stuck in traffic", "ham"),
    ("URGENT! You have won a 1 week FREE membership", "spam"),
    ("Can you send me the report by evening?", "ham"),
    ("You have been chosen to receive $1000 cash", "spam"),
    ("Happy birthday! Have a great day", "ham"),
] * 30 # repeat to make bigger

texts, labels = zip(*messages)
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

vec = TfidfVectorizer()
X_train_vec = vec.fit_transform(X_train)
X_test_vec = vec.transform(X_test)

model = MultinomialNB()
model.fit(X_train_vec, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test_vec))*100:.1f}%")

def check(msg):
    pred = model.predict(vec.transform([msg]))[0]
    print(f"'{msg}' -> {pred.upper()}")

check("Congratulations you won lottery!")
check("Let's meet at MG Road tomorrow")
try:
    user = input("Type a message to test (or press enter to skip): ")
    if user.strip():
        check(user)
except:
    pass
