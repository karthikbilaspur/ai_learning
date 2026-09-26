# 🚀 AI Learning - 30 ML Projects From Beginner to Production

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Projects-30%20End--to--End-6c5ce7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Level-Beginner%20%E2%86%92%20Advanced-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/IDE-VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white" />
</p>

<p align="center">
  <b>One repo. 30 projects. From your first classifier to RLHF & AI Safety.</b><br>
  All projects run in VSCode. No Kaggle login needed. <code>main.py + requirements.txt + README.md</code> in every folder.
</p>

<p align="center">
  <a href="https://github.com/karthikbilaspur">GitHub: @karthikbilaspur</a> •
  <a href="https://github.com/karthikbilaspur/ai_learning">View Full Repo</a>
</p>

---

## 📚 Complete Roadmap - 30 Projects

### 🌱 Level 1: Beginner (01-10) - Foundations
`ml-projects/beginner/` - Run in VSCode, no Kaggle needed

| # | Project | Type | Core Skill |
| :--- | :--- | :--- | :--- |
| **01** | Iris Flower Classifier | Classification | First ML model, train/test split |
| **02** | Bangalore House Price | Regression | EDA, Linear Regression |
| **03** | Spam SMS Detector | NLP | TF-IDF, Naive Bayes |
| **04** | Titanic Survival | Classic Kaggle | Feature Engineering |
| **05** | Handwritten Digit Recognition | Computer Vision | MNIST, CNN |
| **06** | Movie Review Sentiment | Sentiment Analysis | NLP Classification |
| **07** | Customer Segmentation | Unsupervised | K-Means, Elbow Method |
| **08** | Diabetes Prediction | Medical Binary | Healthcare ML |
| **09** | Stock Price Predictor | Time Series | Forecasting |
| **10** | Cats vs Dogs | Transfer Learning | CNN Transfer Learning |

### ⚡ Level 2: Intermediate (11-20) - Real-World & Production
`ml-projects/intermediate/` - Real-world datasets, interview-ready

| # | Project | Domain | Problem Type |
| :--- | :--- | :--- | :--- |
| **11** | Customer Segmentation (Advanced) | Marketing | RFM + K-Means |
| **12** | News Topic Classifier | NLP | Multi-class Classification |
| **13** | Used Car Price Prediction | Regression | XGBoost, Encoding |
| **14** | Credit Card Anomaly Detector | FinTech / Fraud | Isolation Forest, SMOTE |
| **15** | Air Quality Prediction | Environment | AQI, Random Forest |
| **16** | Employee Attrition Prediction | HR Analytics | SHAP, Class Imbalance |
| **17** | Demand Forecasting | Supply Chain | ARIMA, Prophet |
| **18** | Fake Review Detection | Trust & Safety | NLP + Metadata |
| **19** | Traffic Accident Severity | Risk / Safety | Multi-class Risk |
| **20** | Movie Recommendation System | Recommender | Collaborative Filtering |

### 🔬 Level 3: Advanced (21-30) - Research to Production [L1 Fixed]
`ml-projects/advanced/` - Research implementations fixed to run end-to-end

| # | Project | Entry Point | Needs Network? | Core Concept |
| :--- | :--- | :--- | :--- | :--- |
| **21** | Self-Supervised Contrastive (SimCLR) | `src/train.py`, `src/eval_linear.py` | CIFAR-10 download | ResNet-18, Linear Probe |
| **22** | Federated Learning + DP | `src/main.py` or `server.py`+`client.py` | CIFAR-10 download | FedAvg, FedProx, DP-SGD |
| **23** | Neural Architecture Search | `src/controller.py` | MNIST download | RNN Controller |
| **24** | GNN Fraud Detection | `src/make_data.py` → `src/train.py` | **No - Synthetic** | Synthetic Graph, GNN |
| **25** | LLM Eval Harness | `src/main.py` | Model-dependent | Calibration, Toxicity |
| **26** | Synthetic Data Diffusion | `make_data.py`, `train.py`, `generate.py`, `evaluate_synthetic.py` | **No - Synthetic** | DDPM |
| **27** | Retrieval-Augmented Time Series | `make_data.py` → `train.py` | **No - Synthetic** | RAG + Transformer |
| **28** | Reward Model for RLHF | `make_data.py` → `train_rm.py` | Small HF model | Pairwise, DPO-ready |
| **29** | Quantization / Pruning / Edge | `src/main.py` | Small HF model | INT8, Structured Pruning |
| **30** | AI Safety Red Teaming | `src/main.py --target stub` | **No** (stub) | ASR, Safety Suite |

---

## 🚀 How to Run

### Beginner & Intermediate (01-20)

```bash
# Any project follows same 3 commands
cd 01-iris-flower-classifier
pip install -r requirements.txt
python main.py
```

> Tip: Open root in VSCode + use Jupyter extension to run `.py` as `# %%` cells.

### Advanced (21-30)

```bash
pip install -r requirements.txt
# requirements.txt was trimmed to only what code actually imports
# (removed unused mlflow, wandb, sdv, nni, dgl, fastapi, qdrant-client etc.)

# Fast offline check - synthetic projects + Safety stub
bash tests/smoke_test.sh

# Full run with downloads/training
bash tests/smoke_test.sh --full
```

> **Offline-first:** Projects 24, 26, 27, 28, 30 (--target stub) run 100% offline with synthetic data. No API keys needed.

---

## 📁 Folder Structure

```
ai_learning/
├── ml-projects/
│   ├── beginner/               # 01-10
│   │   ├── 01-iris-flower-classifier/
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   └── README.md
│   │   └── ...
│   ├── intermediate/           # 11-20
│   │   ├── 11_customer_segmentation/
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   └── README.md
│   │   └── ...
│   └── advanced/               # 21-30 [L1 Fixed]
│       ├── 21_simclr/
│       │   ├── src/train.py
│       │   ├── src/eval_linear.py
│       │   ├── src/make_data.py
│       │   └── checkpoints/
│       └── ...
└── README.md                   # This file
```

---

## 🛠️ What "L1 Fixed" Means (Advanced Only)

Advanced projects originally had 7 recurring gaps. All closed:

1.  **No Data → Now Has Data:** `make_data.py` generates structured synthetic data or wires CIFAR-10/MNIST
2.  **No Config → Configurable:** Added `argparse` CLIs + `config.py`
3.  **No Checkpointing → Saves:** Training saves best/last to `checkpoints/`
4.  **No Real Eval → Real Metrics:** Train/val/test splits + promised metrics (F1/AUC, linear-probe accuracy, pairwise accuracy, MAE, ASR) not just train loss
5.  **Gated Models → Open Defaults:** Swapped `meta-llama/Meta-Llama-3-8B` → `distilgpt2`, `Llama-Guard` → `unitary/toxic-bert`. ResNet-50 → ResNet-18 for CIFAR-32
6.  **Stub Functions → Working:** Implemented `structured_prune_heads()` (29) + DP wrapper in `strategy.py` (22)
7.  **Disconnected Pieces → End-to-End:** Added `main.py` that chains modules

See each project's README for specific fixes and `LEVEL2_UPGRADE_GUIDE.md` for next level.

---

## 🧠 Learning Path

**For Zero to Job-Ready:**

**Phase 1 - Beginner (Week 1-2):** 01 → 04 → 02 → 08 → 07 → 03 + 06 → 05 → 10 → 09
Learn classification, regression, cleaning, clustering, NLP, CV.

**Phase 2 - Intermediate (Week 3-4):** 11 & 16 → 13 & 15 → 12 & 18 → 14 & 19 → 17 & 20
Learn imbalance handling, text preprocessing, time features, business interpretation. Projects 14, 16, 18, 20 are interview gold.

**Phase 3 - Advanced (Week 5-8):** 24, 26, 27, 30 (offline) → 21, 22, 23 (CIFAR/MNIST) → 28, 29, 25 (LLM stack)
Learn research implementation, federated, GNN, diffusion, RAG, RLHF, quantization, safety. If you can explain 21, 22, 28 you're senior ML.

---

## 🛠️ Tech Stack

**All Levels:** Python, Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn
**Intermediate:** XGBoost, SMOTE, SHAP, NLTK/spaCy, Statsmodels/Prophet
**Advanced:** PyTorch, Transformers (HF), ResNet-18, FedAvg, DDPM, Cosine Similarity, INT8 Quantization, Toxic-Bert

---

## 👨‍💻 Author

**Karthik Bilaspur**
- GitHub: [@karthikbilaspur](https://github.com/karthikbilaspur)
- Repo: [ai_learning](https://github.com/karthikbilaspur/ai_learning)

Structure:
- Beginner: `/tree/main/ml-projects/beginner`
- Intermediate: `/tree/main/ml-projects/intermediate`
- Advanced: `/tree/main/ml-projects/advanced`

If this saved you time, please give a ⭐!

---

## 📄 License

MIT License - Use for learning, teaching, portfolio, and research.

> **What's Next?** Level-2 upgrades: Stronger baselines, ablations, leakage-safe splits, multi-objective NAS, FedProx diagnostics, conditional diffusion, Transformer forecasting, DPO, compression benchmarking, structured safety eval. See `LEVEL2_UPGRADE_GUIDE.md`.
