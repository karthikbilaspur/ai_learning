# 🚀 10 Intermediate ML Projects - Real-World Datasets & Production Code

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-orange?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-10%20Projects%20Ready-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/IDE-VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white" />
</p>

<p align="center">
  <b>Level up from tutorials to real-world problem solving.</b><br>
  No Kaggle login needed. All projects run in VSCode with <code>main.py + requirements.txt + README.md</code>
</p>

<p align="center">
  <a href="https://github.com/karthikbilaspur">GitHub: @karthikbilaspur</a> • 
  <a href="https://github.com/karthikbilaspur/ai_learning/tree/main/ml-projects/intermediate">View on GitHub</a>
</p>

---

## 📚 What's Inside

This is **Part 2** of the `ai_learning` roadmap. These 10 projects are focused on **real-world use cases** that companies actually hire for - fraud detection, HR analytics, recommendation systems, and more.

| # | Project | Domain | Problem Type | Key Skills |
| :--- | :--- | :--- | :--- | :--- |
| **11** | **Customer Segmentation** | Marketing | Unsupervised | K-Means, RFM Analysis, Elbow Method |
| **12** | **News Topic Classifier** | NLP | Multi-class Classification | TF-IDF, Naive Bayes, NLTK / spaCy |
| **13** | **Used Car Price Prediction** | Regression | Regression | Feature Engineering, XGBoost, Encoding |
| **14** | **Credit Card Anomaly Detector** | FinTech / Fraud | Anomaly Detection | Isolation Forest, SMOTE, Imbalanced Data |
| **15** | **Air Quality Prediction** | Environment | Regression / Time Series | AQI, Random Forest, Correlation Analysis |
| **16** | **Employee Attrition Prediction** | HR Analytics | Binary Classification | Class Imbalance, SHAP, Business Insights |
| **17** | **Demand Forecasting** | Supply Chain | Time Series | ARIMA, Prophet, Seasonality |
| **18** | **Fake Review Detection** | Trust & Safety | NLP + Classification | Text Cleaning, Sentiment + Metadata |
| **19** | **Traffic Accident Severity** | Risk / Safety | Multi-class Classification | EDA, Feature Importance, Risk Factors |
| **20** | **Movie Recommendation System** | Recommender | Collaborative Filtering | Cosine Similarity, Content-Based + CF |

---

## 🛠️ Tech Stack

**Core:** `Python, Pandas, NumPy, Scikit-Learn`
**NLP:** `NLTK / spaCy, TF-IDF, CountVectorizer`
**Time Series:** `Statsmodels, Prophet`
**Advanced:** `XGBoost, Imbalanced-Learn (SMOTE), SHAP`
**Viz:** `Matplotlib, Seaborn, Plotly`

---

## 🚀 How to Run Any Project

Every project follows the exact same structure:

```bash
# 1. Go to any project folder
cd 11_customer_segmentation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

> **Tip:** Open the root folder `intermediate` in VSCode and use the Jupyter extension to run `.py` files as interactive cells with `# %%`

### 📁 Folder Structure (for each project)

```
11_customer_segmentation/
├── main.py              # Fully working, commented code
├── requirements.txt     # All dependencies
├── README.md            # Project-specific explanation
└── data/ or dataset.csv # (if applicable, auto-downloaded or included)
```

---

## 🎯 Learning Path

**Recommended order if you're doing this after Beginner:**

1.  **Start with 11 & 16** - Customer & Employee - Classic business analytics
2.  **Then 13 & 15** - Regression deep-dive with real-world pricing/environmental data
3.  **Then 12 & 18** - NLP - News + Fake Reviews (same tools, different complexity)
4.  **Then 14 & 19** - Imbalanced & Risk classification - Learn to handle real-world messy data
5.  **Finish with 17 & 20** - Time Series + Recommender - Most interview-relevant

---

## 💡 What Makes This Intermediate?

Unlike beginner projects (Iris, Titanic), these projects include:
- Handling **imbalanced datasets** (Fraud, Attrition)
- **Text preprocessing** beyond basics
- **Time-based features** & seasonality
- **Business interpretation** - not just accuracy, but *why*
- Code ready to show in **interviews & portfolio**

---

## 🤝 For Recruiters & Portfolio

If you're using this for your portfolio:
- Each `main.py` is interview-ready and fully commented
- Focus on the README inside each folder - it explains business problem + solution
- Projects 14, 16, 18, 20 are high-impact talking points in ML interviews

---

## 👨‍💻 Author

**Karthik Bilaspur**
- GitHub: [@karthikbilaspur](https://github.com/karthikbilaspur)
- Repo: [ai_learning/ml-projects/intermediate](https://github.com/karthikbilaspur/ai_learning/tree/main/ml-projects/intermediate)

If this helped you, please give a ⭐ on GitHub!

---

## 📄 License

MIT License - feel free to use for learning, teaching, and portfolio.

> **Next Up:** Advanced Projects - MLOps, Deployment with FastAPI + Docker
