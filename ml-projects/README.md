# Machine Learning Projects

> A progressive, hands-on machine learning track covering classical ML, NLP, computer vision, time series, recommender systems, deep learning, generative modeling, federated learning, LLM evaluation, model optimization, and AI safety.

This directory is the **Machine Learning track** of the [`ai_learning`](https://github.com/karthikbilaspur/ai_learning) repository.

The projects are organized as a progression:

```text
Beginner
   │
   ├── Classification
   ├── Regression
   ├── NLP
   ├── Computer Vision
   ├── Clustering
   └── Time Series
        │
        ▼
Intermediate
   │
   ├── Better datasets
   ├── Cross-validation
   ├── Model comparison
   ├── Hyperparameter tuning
   ├── Explainability
   ├── Imbalanced learning
   ├── Time-series validation
   └── Interactive Gradio applications
        │
        ▼
Advanced
   │
   ├── Self-supervised learning
   ├── Federated learning + DP
   ├── Neural architecture search
   ├── Graph neural networks
   ├── LLM evaluation
   ├── Diffusion models
   ├── Retrieval-augmented forecasting
   ├── Preference learning / RLHF
   ├── Quantization + pruning
   └── AI safety / red teaming
```

The objective is not simply to collect machine-learning algorithms. Each level progressively introduces the engineering practices required to turn an ML experiment into a more reliable system.

---

## Table of Contents

* [Learning Philosophy](#learning-philosophy)
* [Project Levels](#project-levels)
* [Project Catalog](#project-catalog)

  * [Beginner: 01–10](#beginner-01-10)
  * [Intermediate: 11–20](#intermediate-11-20)
  * [Advanced: 21–30](#advanced-21-30)
* [Getting Started](#getting-started)
* [Beginner Setup](#beginner-setup)
* [Intermediate Setup](#intermediate-setup)
* [Advanced Setup](#advanced-setup)
* [Advanced Testing](#advanced-testing)
* [Datasets](#datasets)
* [Evaluation Philosophy](#evaluation-philosophy)
* [Reproducibility](#reproducibility)
* [Project Structure](#project-structure)
* [What Each Level Teaches](#what-each-level-teaches)
* [Known Limitations](#known-limitations)
* [Future Improvements](#future-improvements)
* [Learning Path](#learning-path)

---

# Learning Philosophy

The projects follow a simple engineering loop:

```text
Understand
    ↓
Implement
    ↓
Evaluate
    ↓
Break
    ↓
Analyze
    ↓
Improve
    ↓
Deploy / Experiment Further
```

A model producing a high accuracy number is not automatically a good ML system.

As the projects progress, the focus expands from:

* choosing an algorithm
* preparing data
* training a model

toward:

* selecting appropriate metrics
* preventing data leakage
* cross-validation
* hyperparameter tuning
* explainability
* model comparison
* reproducibility
* checkpointing
* deployment
* latency
* privacy
* safety
* failure analysis

---

# Project Levels

| Level           | Projects | Primary Focus                     | Typical Output                                 |
| --------------- | -------: | --------------------------------- | ---------------------------------------------- |
| 🟢 Beginner     |    01–10 | ML fundamentals                   | Python training scripts                        |
| 🟡 Intermediate |    11–20 | Practical ML engineering          | Trained models + evaluation + Gradio demos     |
| 🔴 Advanced     |    21–30 | Modern ML/AI research engineering | Training pipelines + checkpoints + experiments |

---

# Project Catalog

## Beginner — Projects 01–10

The beginner track focuses on understanding the fundamental ML workflow without introducing unnecessary infrastructure.

Each project generally contains:

```text
project/
├── main.py
├── requirements.txt
├── README.md
└── optional plots / outputs
```

### 01 — Iris Flower Classifier

**Path:** [`01-iris-flower-classifier`](./beginner/01-iris-flower-classifier)

**Topic:** Classification

A small classification problem designed to introduce the basic supervised-learning workflow.

**Concepts:**

* Classification
* Feature/target separation
* Train/test split
* Model training
* Prediction
* Evaluation
* Visualization

**Run:**

```bash
cd beginner/01-iris-flower-classifier
pip install -r requirements.txt
python main.py
```

---

### 02 — Bangalore House Price

**Path:** [`02-bangalore-house-price`](./beginner/02-bangalore-house-price)

**Topic:** Regression

Introduces regression by predicting house prices from property-related features.

The current implementation uses synthetic data so that the project can run offline.

**Concepts:**

* Regression
* Feature engineering
* Continuous targets
* Prediction error
* Model evaluation

**Run:**

```bash
cd beginner/02-bangalore-house-price
pip install -r requirements.txt
python main.py
```

**Next step:** Replace the synthetic dataset with a real Bangalore housing dataset.

---

### 03 — Spam SMS Detector

**Path:** [`03-spam-sms-detector`](./beginner/03-spam-sms-detector)

**Topic:** NLP + Classification

A text-classification project using:

```text
SMS text
   ↓
TF-IDF
   ↓
Naive Bayes
   ↓
Spam / Not Spam
```

**Concepts:**

* Natural language processing
* Text preprocessing
* TF-IDF
* Naive Bayes
* Binary classification

**Run:**

```bash
cd beginner/03-spam-sms-detector
pip install -r requirements.txt
python main.py
```

---

### 04 — Titanic Survival

**Path:** [`04-titanic-survival`](./beginner/04-titanic-survival)

**Topic:** Binary Classification

The classic Titanic survival prediction problem.

**Concepts:**

* Tabular ML
* Binary classification
* Feature preprocessing
* Missing values
* Categorical variables
* Model evaluation

The project is prepared to be connected to the real Kaggle Titanic dataset.

---

### 05 — Handwritten Digit Recognition

**Path:** [`05-handwritten-digit-recognition`](./beginner/05-handwritten-digit-recognition)

**Topic:** Computer Vision

The lightweight implementation uses the scikit-learn digits dataset.

**Concepts:**

* Image classification
* Pixel features
* Multiclass classification
* Prediction visualization

A TensorFlow/MNIST CNN implementation can be used as a future extension.

---

### 06 — Movie Review Sentiment

**Path:** [`06-movie-review-sentiment`](./beginner/06-movie-review-sentiment)

**Topic:** Sentiment Analysis

Introduces text classification through movie-review sentiment.

**Concepts:**

* NLP
* Text classification
* Sentiment analysis
* Feature extraction
* Binary prediction

The project can be upgraded to the larger IMDB dataset for more realistic experimentation.

---

### 07 — Customer Segmentation

**Path:** [`07-customer-segmentation`](./beginner/07-customer-segmentation)

**Topic:** Unsupervised Learning

Customer segmentation using K-Means clustering.

```text
Customer data
      ↓
Feature representation
      ↓
K-Means
      ↓
Customer clusters
      ↓
Visualization
```

**Concepts:**

* Unsupervised learning
* K-Means
* Clustering
* Cluster visualization
* Customer analytics

---

### 08 — Diabetes Prediction

**Path:** [`08-diabetes-prediction`](./beginner/08-diabetes-prediction)

**Topic:** Binary Classification

Introduces a medical prediction problem using tabular features.

**Concepts:**

* Binary classification
* Feature preprocessing
* Classification metrics
* Model interpretation

> This is an educational ML project, not a clinical diagnostic system.

---

### 09 — Stock Price Predictor

**Path:** [`09-stock-price-predictor`](./beginner/09-stock-price-predictor)

**Topic:** Time Series

A basic stock-price prediction experiment.

The default workflow can run with synthetic data. `yfinance` can be used for live market-data experimentation.

**Concepts:**

* Time-series data
* Regression
* Sequential features
* Prediction visualization

> Predictions from this project should not be interpreted as financial advice.

---

### 10 — Cats vs Dogs Classifier

**Path:** [`10-cats-vs-dogs-classifier`](./beginner/10-cats-vs-dogs-classifier)

**Topic:** Computer Vision + Transfer Learning

Introduces image classification and transfer learning.

**Concepts:**

* Image preprocessing
* CNNs
* Transfer learning
* Binary image classification
* Model inference

The project includes a lightweight demo path and a more complete transfer-learning path.

---

# Intermediate — Projects 11–20

The intermediate track is a significant step beyond the beginner projects.

Instead of simply training one model and printing a metric, the projects introduce:

* multiple candidate models
* cross-validation
* more appropriate metrics
* hyperparameter tuning
* explainability
* real datasets where available
* synthetic datasets with explicit limitations where real data was not available
* interactive Gradio demos

The standard workflow becomes:

```text
Dataset
   ↓
Preprocessing
   ↓
Train / Validation Strategy
   ↓
Multiple Models
   ↓
Cross-Validation
   ↓
Model Selection
   ↓
Hyperparameter Tuning
   ↓
Held-Out Evaluation
   ↓
Explainability / Diagnostics
   ↓
Interactive Demo
```

---

### 11 — Customer Segmentation

**Path:** [`11_customer_segmentation`](./intermediate/11_customer_segmentation)

**Dataset:** Mall Customers

**Methods:**

* K-Means
* Silhouette analysis
* Elbow analysis
* PCA
* Automatic cluster profiling
* Gradio

The project moves from the beginner synthetic segmentation example to a real 200-customer dataset.

Outputs include:

* segmentation model
* segmented customer CSV
* cluster profiles
* cluster names
* cluster-selection plots
* PCA visualization

---

### 12 — News Topic Classifier

**Path:** [`12_news_topic_classifier`](./intermediate/12_news_topic_classifier)

**Topic:** NLP Classification

Compares:

* Logistic Regression
* Linear SVM
* SGD

using stratified cross-validation.

The project also produces:

* confusion matrix
* per-class F1
* saved model
* Gradio demo

### Important limitation

The current corpus is still synthetic/templated. Its near-perfect performance should therefore **not** be interpreted as evidence of real-world news-classification performance.

Recommended next datasets:

* AG News
* BBC News
* 20 Newsgroups

---

### 13 — Used Car Price Prediction

**Path:** [`13_used_car_price_prediction`](./intermediate/13_used_car_price_prediction)

**Dataset:** CarPrice_Assignment

**Models:**

* Random Forest
* Gradient Boosting
* XGBoost

The project adds:

* data cleaning
* brand extraction
* cross-validation
* randomized hyperparameter search
* SHAP explainability
* Gradio prediction interface

The documented held-out result is approximately:

```text
MAE  ≈ $1,331
R²   ≈ 0.955
```

---

### 14 — Credit Card Spending Anomaly Detector

**Path:** [`14_credit_card_anomaly_detector`](./intermediate/14_credit_card_anomaly_detector)

**Topic:** Unsupervised Anomaly Detection

Compares:

* Isolation Forest
* One-Class SVM
* Local Outlier Factor

Evaluation includes:

* Precision
* Recall
* PR-AUC
* ROC-AUC

Features include transaction-related signals such as:

* amount
* hour
* distance from home
* merchant risk
* transaction velocity

### Important limitation

The current anomalies are synthetic and relatively easy to separate.

A natural next step is the real Credit Card Fraud Detection dataset.

---

### 15 — Air Quality Prediction

**Path:** [`15_air_quality_prediction`](./intermediate/15_air_quality_prediction)

**Topic:** Regression

Compares:

* Random Forest
* Gradient Boosting
* XGBoost

Adds:

* cross-validation
* hyperparameter tuning
* residual diagnostics
* SHAP explanations
* Gradio inference

Documented held-out result:

```text
MAE ≈ 4.7
R²  ≈ 0.968
```

### Important limitation

The current data is synthetic and does not contain genuine temporal dependencies.

A real hourly air-quality dataset would make the problem substantially more realistic.

---

### 16 — Employee Attrition Prediction

**Path:** [`16_employee_attrition_prediction`](./intermediate/16_employee_attrition_prediction)

**Dataset:** IBM HR Analytics Attrition

**Models:**

* Logistic Regression
* Random Forest
* XGBoost

The project explicitly handles class imbalance and uses PR-AUC as an important evaluation metric.

Documented held-out results:

```text
ROC-AUC ≈ 0.78
PR-AUC  ≈ 0.50
```

The project also includes SHAP-based interpretation.

> Predictions should be treated as an educational modeling exercise rather than a basis for automated employment decisions.

---

### 17 — Retail Demand Forecasting

**Path:** [`17_demand_forecasting`](./intermediate/17_demand_forecasting)

**Topic:** Time-Series Forecasting

Introduces a more appropriate validation strategy:

```text
Training history
       ↓
Forecast window
       ↓
Evaluate
       ↓
Expand training history
       ↓
Forecast again
```

This is implemented using walk-forward validation.

Features include:

* holidays
* promotions
* temporal signals

The project also experiments with quantile regression to generate prediction intervals.

Documented results:

```text
Walk-forward MAE ≈ 6.6
Holdout MAE      ≈ 5.9
MAPE             ≈ 4.1%
```

### Important limitation

The documented 80% prediction interval achieved only around 52% empirical coverage in testing.

Therefore, the interval should currently be considered **illustrative rather than calibrated**.

---

### 18 — Fake Review Detection

**Path:** [`18_fake_review_detection`](./intermediate/18_fake_review_detection)

**Topic:** NLP + Metadata Classification

The project compares:

```text
Text only
   vs.
Text + reviewer metadata
```

Metadata includes signals such as:

* rating deviation
* posting frequency

### Important limitation

The current dataset remains synthetic and uses a small set of fake-review templates.

The system should therefore be understood as a **screening experiment**, not a system that can reliably determine whether a real review is fake.

---

### 19 — Traffic Accident Severity

**Path:** [`19_traffic_accident_severity`](./intermediate/19_traffic_accident_severity)

**Topic:** Ordinal / Multiclass Classification

Predicts:

```text
Low
Medium
High
```

The project compares:

* Random Forest multiclass classification
* Ordinal classification

It also evaluates a particularly important error:

```text
P(predicted Low | actual High)
```

This demonstrates an important ML principle:

> The most useful metric is often determined by the cost of a specific failure, not by generic accuracy.

---

### 20 — Movie Recommendation System

**Path:** [`20_movie_recommendation_system`](./intermediate/20_movie_recommendation_system)

**Dataset:** IMDB movie metadata

The recommender combines:

* genres
* plot keywords
* director
* top-billed actors

using a TF-IDF-based content representation.

It then combines content similarity with a popularity/quality prior.

The project also includes:

* recommendation evaluation
* genre-overlap sanity check
* Gradio interface
* adjustable content/popularity weighting

Documented genre-overlap result:

```text
≈ 78.5%
```

A future version can introduce collaborative filtering using MovieLens ratings.

---

# Advanced — Projects 21–30

The advanced track moves beyond standard tabular ML and into modern ML/AI research engineering.

The projects introduce concepts such as:

* self-supervised learning
* distributed/federated learning
* differential privacy
* neural architecture search
* graph neural networks
* LLM evaluation
* diffusion models
* retrieval-augmented forecasting
* preference optimization
* model compression
* AI safety

Unlike the beginner and intermediate projects, several advanced projects require:

* PyTorch
* Hugging Face models
* dataset downloads
* GPU resources for practical training
* more involved experiment management

---

### 21 — Self-Supervised Contrastive Learning

**Path:** [`21_self_supervised_contrastive`](./advance/21_self_supervised_contrastive)

**Method:** SimCLR

The project implements contrastive representation learning on CIFAR-10.

Architecture:

```text
Image
  ↓
Augmentation 1 ──┐
                 ├──► Shared Encoder ──► Projection Head
  Image           │
  ↓              ─┘
Augmentation 2
```

Includes:

* CIFAR-sized ResNet-18
* NT-Xent loss
* configurable training
* checkpointing
* resume support
* linear-probe evaluation

**Entry points:**

```bash
python src/train.py
python src/eval_linear.py
```

---

### 22 — Federated Learning + Differential Privacy

**Path:** [`22_federated_learning`](./advance/22_federated_learning)

**Technology:** Flower

Simulates federated learning across multiple clients.

Supports:

* IID client partitions
* non-IID label-skew partitions
* FedAvg
* differentially private aggregation
* client/server execution
* in-process simulation

Conceptually:

```text
Client 1 ─┐
Client 2 ─┤
Client 3 ─┼──► Federated Aggregation ──► Global Model
Client 4 ─┤
Client 5 ─┘
```

Run:

```bash
python src/main.py --num_clients 5 --num_rounds 10
```

With DP:

```bash
python src/main.py \
    --num_clients 5 \
    --num_rounds 10 \
    --dp \
    --clip_norm 1.0 \
    --noise_multiplier 0.1
```

---

### 23 — Neural Architecture Search

**Path:** [`23_neural_architecture_search`](./advance/23_neural_architecture_search)

**Technology:** Optuna

Searches an MLP architecture space on MNIST.

The pipeline is:

```text
Search Space
     ↓
Optuna Trials
     ↓
Short Training
     ↓
Validation Score
     ↓
Best Architecture
     ↓
Full Retraining
     ↓
Checkpoint
```

Run:

```bash
python src/controller.py \
    --n_trials 20 \
    --epochs 3 \
    --final_epochs 10
```

---

### 24 — GNN Fraud Detection

**Path:** [`24_gnn_fraud_detection`](./advance/24_gnn_fraud_detection)

**Topic:** Graph Neural Networks

Builds a transaction graph containing users and transactions.

Includes:

* synthetic transaction generation
* graph construction
* feature normalization
* train/validation/test masks
* FraudGAT
* FraudGraphSAGE
* class-imbalance handling
* F1
* AUC
* model checkpointing

Generate data:

```bash
python src/make_data.py \
    --n_users 200 \
    --n_tx 5000
```

Train:

```bash
python src/train.py \
    --model gat \
    --epochs 100
```

---

### 25 — LLM Evaluation Harness

**Path:** [`25_llm_eval_harness`](./advance/25_llm_eval_harness)

**Topic:** Automated LLM Evaluation

Provides a framework for evaluating model outputs across multiple dimensions.

Evaluation areas include:

* hallucination proxy
* toxicity
* TruthfulQA accuracy
* counterfactual bias probes
* LLM-as-a-judge scoring

Supported model modes include:

```text
Echo / offline stub
        │
        ├── Local Hugging Face model
        │
        └── OpenAI model
```

Offline example:

```bash
python src/main.py \
    --model echo \
    --n 5
```

Hugging Face example:

```bash
python src/main.py \
    --model hf \
    --model_id distilgpt2 \
    --n 10
```

OpenAI judge mode requires an API key.

---

### 26 — Synthetic Data Diffusion

**Path:** [`26_synthetic_data_diffusion`](./advance/26_synthetic_data_diffusion)

**Topic:** Tabular Diffusion

Implements a tabular diffusion model inspired by TabDDPM.

Pipeline:

```text
Real Tabular Data
       ↓
Forward Noise Process
       ↓
Denoising Model
       ↓
Reverse Diffusion
       ↓
Synthetic Data
```

The project evaluates:

* fidelity
* utility
* privacy-related distance metrics

Run:

```bash
python src/make_data.py --n_samples 3000

python src/train.py \
    --csv data/real.csv \
    --epochs 100

python src/generate.py \
    --n_samples 1000

python src/evaluate_synthetic.py \
    --real_csv data/real.csv \
    --synth_csv data/synthetic.csv
```

---

### 27 — Retrieval-Augmented Time-Series Forecasting

**Path:** [`27_retrieval_time_series`](./advance/27_retrieval_time_series)

**Topic:** Retrieval-Augmented Forecasting

Combines time-series forecasting with retrieval of similar historical windows.

A major focus is avoiding retrieval leakage.

```text
Historical Training Windows
          ↓
       Retriever
          ↓
Similar Historical Patterns
          ↓
Forecasting Model
          ↓
Future Prediction
```

The retrieval corpus is constructed from training data, while test windows are evaluated separately.

Run:

```bash
python src/make_data.py --length 5000

python src/train.py \
    --series_path data/series.npy \
    --epochs 30
```

---

### 28 — Reward Model for RLHF

**Path:** [`28_reward_model_rlhf`](./advance/28_reward_model_rlhf)

**Topic:** Preference Learning

The project trains a reward model using preference pairs:

```text
Prompt
 ├── Chosen response
 └── Rejected response
          ↓
     Reward Model
          ↓
Preference Score
```

Uses a Bradley-Terry style preference objective.

The default model is an open `distilgpt2` checkpoint rather than a gated large model.

Run:

```bash
python src/make_data.py \
    --n 500

python src/train_rm.py \
    --jsonl data/preferences.jsonl \
    --base distilgpt2
```

Evaluation includes pairwise preference accuracy.

---

### 29 — Quantization, Pruning & Edge Deployment

**Path:** [`29_quantization_pruning_edge`](./advance/29_quantization_pruning_edge)

**Topic:** Model Optimization

Explores techniques for making models smaller and more efficient.

Includes:

* quantization
* structured pruning
* benchmarking
* latency measurement
* memory measurement
* before/after comparison

The pruning implementation ranks attention heads and removes weaker heads.

Run:

```bash
python src/main.py \
    --model_id distilgpt2 \
    --prune_amount 0.3
```

The project demonstrates an important deployment principle:

```text
Model Quality
      ↕
Model Size
      ↕
Latency
      ↕
Memory
```

These trade-offs need to be measured rather than assumed.

---

### 30 — AI Safety Red Teaming

**Path:** [`30_ai_safety_red_teaming`](./advance/30_ai_safety_red_teaming)

**Topic:** AI Safety + Adversarial Evaluation

Provides an automated red-team experiment for testing model behavior against attack goals.

Components include:

* attack goals
* target models
* attack strategies
* guardrails
* attack success rate
* safety metrics

The project supports an offline stub target, making the basic experiment runnable without external model access.

Run:

```bash
python src/main.py \
    --target stub
```

For a model-backed experiment:

```bash
python src/main.py \
    --target hf \
    --guardrail
```

The repository explicitly treats simple keyword guardrails and attack heuristics as **proxies**, not substitutes for comprehensive safety evaluation.

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/karthikbilaspur/ai_learning.git
cd ai_learning/ml-projects
```

Choose a level:

```bash
cd beginner
```

or:

```bash
cd intermediate
```

or:

```bash
cd advance
```

---

# Beginner Setup

The beginner projects are intentionally lightweight.

Install the shared dependencies:

```bash
cd beginner
pip install -r requirements-all.txt
```

The shared requirements include:

```text
scikit-learn
pandas
numpy
matplotlib
seaborn
yfinance
```

Individual projects also contain their own `requirements.txt`.

For example:

```bash
cd 01-iris-flower-classifier
pip install -r requirements.txt
python main.py
```

---

# Intermediate Setup

Each intermediate project is self-contained.

```bash
cd intermediate/11_customer_segmentation
pip install -r requirements.txt
python train.py
python app.py
```

The standard workflow is:

```bash
python train.py
```

followed by:

```bash
python app.py
```

The Gradio application normally starts on:

```text
http://localhost:7860
```

The training script generally handles:

* data loading
* preprocessing
* model training
* evaluation
* model persistence
* visualization

---

# Advanced Setup

Install the shared advanced dependencies:

```bash
cd advance
pip install -r requirements.txt
```

The advanced dependency stack includes technologies such as:

* PyTorch
* TorchVision
* Transformers
* Accelerate
* PEFT
* TRL
* Hugging Face Datasets
* scikit-learn
* XGBoost
* LightGBM
* Flower
* Opacus
* PyTorch Geometric
* Optuna
* Lightly
* timm
* SciPy
* Matplotlib
* pytest
* ONNX
* ONNX Runtime
* Optimum

Some projects additionally require:

* internet access
* model downloads
* dataset downloads
* Hugging Face access
* OpenAI API access
* GPU resources

---

# Advanced Testing

The advanced track includes a smoke-test script:

```bash
cd advance
bash tests/smoke_test.sh
```

The default test is designed to be relatively fast and mostly offline.

It performs:

* Python compilation checks
* synthetic-data generation
* dependency-light project checks
* an offline safety-red-team run

For example:

```text
21 → syntax checks
22 → syntax checks
23 → syntax checks
24 → synthetic data generation
25 → syntax checks
26 → synthetic data generation
27 → synthetic time series generation
28 → synthetic preference generation
29 → syntax checks
30 → full offline stub run
```

To attempt the download-dependent experiments:

```bash
bash tests/smoke_test.sh --full
```

The full mode requires the necessary dependencies, network access, and model/dataset downloads.

---

# Datasets

The projects deliberately use a mixture of dataset types.

## Standard / Public Datasets

Examples include:

* Iris
* CIFAR-10
* MNIST
* Mall Customers
* CarPrice_Assignment
* IBM HR Analytics Attrition
* IMDB movie metadata

## Synthetic Datasets

Synthetic data is used when:

* a suitable dataset was not included
* network access was unavailable during development
* the project is intended to isolate a particular ML concept

This is particularly relevant to several intermediate and advanced projects.

Synthetic data is useful for pipeline development, but it should **not** be treated as equivalent to real-world validation.

---

# Evaluation Philosophy

One of the major differences between the three levels is how model performance is evaluated.

## Beginner

The emphasis is on understanding the basic workflow:

```text
Train
 ↓
Predict
 ↓
Measure
```

---

## Intermediate

Evaluation becomes more rigorous:

```text
Candidate Models
       ↓
Cross-Validation
       ↓
Model Comparison
       ↓
Hyperparameter Tuning
       ↓
Held-Out Test Set
       ↓
Diagnostics / Explainability
```

Different projects use metrics appropriate to the problem.

Examples include:

* MAE
* R²
* Accuracy
* F1
* ROC-AUC
* PR-AUC
* MAPE
* per-class metrics
* cost-aware error rates
* genre-overlap checks

---

## Advanced

The evaluation philosophy expands further.

Depending on the project, evaluation may include:

* held-out test performance
* linear-probe accuracy
* pairwise preference accuracy
* F1
* ROC-AUC
* PR-AUC
* latency
* memory
* parameter count
* sparsity
* privacy diagnostics
* attack success rate
* safety error rates
* synthetic-data fidelity
* synthetic-data utility
* nearest-neighbor privacy diagnostics

The objective is to avoid treating a single scalar metric as the complete description of a model.

---

# Reproducibility

The advanced projects introduce shared experiment utilities through:

```text
advance/common/experiment.py
```

The shared utilities provide:

* deterministic random seeds
* NumPy seeding
* PyTorch seeding when available
* JSON result persistence
* lightweight experiment timing

A typical experiment should record:

```text
Dataset
Model
Configuration
Seed
Metrics
Runtime
```

The advanced Level-2 upgrade guide further recommends saving experiment results in machine-readable formats such as:

```text
JSON
CSV
```

under project-specific `results/` directories.

---

# Project Structure

At a high level:

```text
ml-projects/
│
├── beginner/
│   ├── 01-iris-flower-classifier/
│   ├── 02-bangalore-house-price/
│   ├── 03-spam-sms-detector/
│   ├── 04-titanic-survival/
│   ├── 05-handwritten-digit-recognition/
│   ├── 06-movie-review-sentiment/
│   ├── 07-customer-segmentation/
│   ├── 08-diabetes-prediction/
│   ├── 09-stock-price-predictor/
│   ├── 10-cats-vs-dogs-classifier/
│   ├── README.md
│   └── requirements-all.txt
│
├── intermediate/
│   ├── 11_customer_segmentation/
│   ├── 12_news_topic_classifier/
│   ├── 13_used_car_price_prediction/
│   ├── 14_credit_card_anomaly_detector/
│   ├── 15_air_quality_prediction/
│   ├── 16_employee_attrition_prediction/
│   ├── 17_demand_forecasting/
│   ├── 18_fake_review_detection/
│   ├── 19_traffic_accident_severity/
│   ├── 20_movie_recommendation_system/
│   └── README.md
│
└── advance/
    ├── 21_self_supervised_contrastive/
    ├── 22_federated_learning/
    ├── 23_neural_architecture_search/
    ├── 24_gnn_fraud_detection/
    ├── 25_llm_eval_harness/
    ├── 26_synthetic_data_diffusion/
    ├── 27_retrieval_time_series/
    ├── 28_reward_model_rlhf/
    ├── 29_quantization_pruning_edge/
    ├── 30_ai_safety_red_teaming/
    ├── common/
    ├── tests/
    ├── LEVEL2_UPGRADE_GUIDE.md
    ├── README.md
    └── requirements.txt
```

---

# What Each Level Teaches

## 🟢 Beginner

### Core ML

* supervised learning
* unsupervised learning
* classification
* regression
* clustering

### Data

* loading datasets
* preprocessing
* feature/target separation
* train/test splitting

### Evaluation

* accuracy
* basic regression metrics
* classification reports
* visual inspection

### Practical Domains

* finance
* housing
* healthcare
* NLP
* computer vision
* customer analytics

---

## 🟡 Intermediate

### Better Modeling

* multiple candidate models
* cross-validation
* hyperparameter tuning
* model selection

### Better Evaluation

* PR-AUC
* ROC-AUC
* MAPE
* per-class metrics
* cost-aware metrics
* walk-forward validation

### Better Understanding

* SHAP
* residual diagnostics
* confusion matrices
* cluster profiling

### Deployment

Every intermediate project includes an interactive Gradio demo.

---

## 🔴 Advanced

### Representation Learning

* SimCLR
* contrastive learning
* linear probing

### Distributed / Private ML

* federated learning
* FedAvg
* differential privacy

### Automated ML

* neural architecture search
* Optuna
* multi-objective optimization

### Graph ML

* GAT
* GraphSAGE
* transaction graphs

### Generative AI

* diffusion models
* synthetic tabular data
* reward models
* preference learning

### LLM Engineering

* LLM evaluation
* LLM-as-a-judge
* hallucination evaluation
* toxicity evaluation
* bias probes

### ML Systems

* retrieval-augmented forecasting
* checkpointing
* latency benchmarking
* model compression

### AI Safety

* red teaming
* jailbreak evaluation
* guardrails
* attack success rate
* safety metrics

---

# Known Limitations

This collection is intentionally educational and experimental.

Not every project represents production-ready ML.

Several limitations are explicitly documented in the project READMEs.

## Synthetic Data

Some intermediate projects use synthetic data because suitable real-data mirrors were not available during development.

This applies particularly to projects such as:

* News Topic Classification
* Credit Card Anomaly Detection
* Air Quality Prediction
* Demand Forecasting
* Fake Review Detection
* Traffic Accident Severity

Synthetic data makes the pipelines reproducible and runnable, but it can produce unrealistically strong metrics.

---

## Near-Perfect Metrics

Very high scores on synthetic datasets should be interpreted cautiously.

For example:

```text
Synthetic dataset
       ↓
Easy-to-learn patterns
       ↓
Very high metric
       ↓
Does NOT necessarily imply
real-world performance
```

The intermediate projects intentionally document these limitations rather than hiding them.

---

## Real-World Validation

A meaningful production ML system generally requires additional work such as:

* larger datasets
* temporal validation
* external validation
* monitoring
* calibration
* drift detection
* fairness analysis
* security testing
* robust error analysis
* domain-specific validation

Those concerns are beyond what these learning projects attempt to completely solve.

---

# Level-2 Research / Engineering Direction

The advanced directory contains a separate:

```text
LEVEL2_UPGRADE_GUIDE.md
```

The Level-2 direction focuses on controlled experiments and stronger research practices.

The proposed improvements include:

### 21 — Self-Supervised Learning

* temperature ablations
* SimSiam comparison
* kNN evaluation
* linear-probe evaluation
* training-time and memory measurement

### 22 — Federated Learning

* FedAvg vs FedProx
* IID vs non-IID
* DP experiments
* privacy diagnostics

> Approximate privacy estimates should not be treated as formal privacy guarantees without a validated privacy accountant.

### 23 — NAS

* accuracy
* parameter count
* CPU latency
* Pareto-frontier analysis

### 24 — GNN Fraud

* chronological splits
* leakage prevention
* F1
* ROC-AUC
* PR-AUC
* heterogeneous graphs

### 25 — LLM Evaluation

* repeated evaluation
* latency statistics
* persistent evaluation datasets
* regression testing

### 26 — Diffusion

* conditional generation
* Gaussian baselines
* fidelity
* utility
* nearest-neighbor analysis

### 27 — Time Series

* Transformer forecasting
* LSTM comparison
* retrieval-augmented Transformer
* chronological evaluation

### 28 — Preference Optimization

* DPO
* reward-model reranking
* preference diagnostics
* SFT comparison

### 29 — Model Compression

* FP32
* dynamic INT8
* magnitude pruning
* latency
* memory
* sparsity

### 30 — AI Safety

* structured attack families
* refusal metrics
* guardrail error rates
* stronger safety judges

---

# Advanced Level-2 Acceptance Criteria

The advanced upgrade guide defines a useful standard for future experiments.

Every project should aim to have:

1. At least one meaningful baseline.
2. At least one controlled ablation.
3. At least three relevant metrics.
4. A fixed random seed.
5. An explicit data split.
6. Machine-readable experiment results.
7. Failure analysis.
8. No train/test or future-data leakage.
9. A reproducible command from a clean environment.

This provides a useful bridge from:

```text
ML Project
    ↓
ML Experiment
    ↓
Controlled Experiment
    ↓
Reproducible Research
```

---

# Learning Path

If you are using this repository as a structured ML curriculum, a reasonable progression is:

## Phase 1 — ML Fundamentals

Start with:

```text
01 → 02 → 03 → 04
```

Learn:

* classification
* regression
* NLP
* tabular ML

---

## Phase 2 — Broaden the Problem Types

Continue with:

```text
05 → 06 → 07 → 08 → 09 → 10
```

Learn:

* computer vision
* sentiment analysis
* clustering
* medical classification
* time series
* transfer learning

---

## Phase 3 — Practical ML Engineering

Move to:

```text
11 → 12 → 13 → 14 → 15
```

Focus on:

* cross-validation
* model comparison
* hyperparameter tuning
* anomaly detection
* explainability

---

## Phase 4 — Real-World Evaluation

Continue with:

```text
16 → 17 → 18 → 19 → 20
```

Focus on:

* class imbalance
* time-series validation
* cost-sensitive evaluation
* recommendation systems
* realistic dataset limitations

---

## Phase 5 — Modern ML

Then move into:

```text
21 → 22 → 23 → 24
```

Learn:

* self-supervised learning
* federated learning
* privacy
* NAS
* graph neural networks

---

## Phase 6 — Modern AI Systems

Finish with:

```text
25 → 26 → 27 → 28 → 29 → 30
```

Learn:

* LLM evaluation
* diffusion
* retrieval-augmented forecasting
* preference learning
* model optimization
* AI safety

---

# The Bigger Picture

The 30 projects are best understood as a progression in **ML engineering maturity**.

```text
                    MACHINE LEARNING
                           │
                           ▼
                  Learn the algorithm
                           │
                           ▼
                    Build a model
                           │
                           ▼
                  Evaluate the model
                           │
                           ▼
              Compare alternative models
                           │
                           ▼
                 Tune the hyperparameters
                           │
                           ▼
                  Explain the predictions
                           │
                           ▼
                 Test failure scenarios
                           │
                           ▼
                Measure system behavior
                           │
                           ▼
                 Improve reproducibility
                           │
                           ▼
                   Deploy the model
                           │
                           ▼
                 Monitor + evaluate
                           │
                           ▼
                   Harden the system
```

The ultimate goal of this track is therefore not simply:

> **"Learn 30 ML algorithms."**

It is:

> **Learn how to build, evaluate, debug, explain, optimize, and eventually productionize machine-learning systems.**

---

# Contributing / Extending a Project

When extending a project, prefer the following workflow:

```text
1. Establish a baseline
2. Define the evaluation metric
3. Create a reproducible split
4. Train candidate models
5. Compare results
6. Perform controlled experiments
7. Analyze failures
8. Save the results
9. Document limitations
10. Add a reproducible command
```

For advanced experiments, also record:

```text
dataset
model
hyperparameters
seed
hardware
training time
evaluation metrics
```

---

# Important Notes

These projects are primarily intended for:

* learning
* experimentation
* portfolio development
* understanding ML workflows
* exploring modern AI techniques

They should not automatically be interpreted as:

* production systems
* clinical decision systems
* financial prediction systems
* employment decision systems
* fraud adjudication systems
* safety-certified AI systems

Real-world deployment requires domain-specific validation, monitoring, security, governance, and additional testing.

---

# Related Repository

This ML track is part of the broader **AI Engineering Lab**:

```text
ai_learning/
│
├── ml-projects/          ← You are here
├── RAG-AGENT/
├── rag_code-v2/
├── talk-to-repo-advanced/
├── ai-agent-9tools-full/
├── ai-gateway/
├── agent-redteam/
├── devops-projects/
└── ...
```

The broader repository explores the progression:

```text
ML Fundamentals
       ↓
LLM Applications
       ↓
RAG
       ↓
Agents
       ↓
Evaluation
       ↓
Security
       ↓
AI Infrastructure
       ↓
DevOps
       ↓
Production-Oriented AI Systems
```

---

## Final Principle

The philosophy behind this ML track can be summarized as:

```text
Understand
    ↓
Build
    ↓
Measure
    ↓
Break
    ↓
Learn
    ↓
Improve
    ↓
Repeat
```

A working model is the beginning of the process—not the end.

