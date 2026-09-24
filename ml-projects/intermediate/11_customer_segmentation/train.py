"""
Level 2 upgrade — Customer Segmentation
- Real dataset (Mall Customers, data/Mall_Customers.csv) instead of synthetic data
- Silhouette score added alongside the elbow method to justify k
- PCA 2D projection for visualization
- Automatic, interpretable cluster naming based on feature profile
- Saves the fitted scaler + KMeans model for reuse in app.py
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import joblib

RANDOM_STATE = 42
DATA_PATH = "data/Mall_Customers.csv"
FEATURES = ["Age", "Annual Income (k$)", "Spending Score (1-100)"]


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def choose_k(X, k_range=range(2, 9)):
    inertias, silhouettes = [], []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = model.fit_predict(X)
        inertias.append(model.inertia_)
        silhouettes.append(silhouette_score(X, labels))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(list(k_range), inertias, marker="o")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inertia")
    axes[0].set_title("Elbow Method")

    axes[1].plot(list(k_range), silhouettes, marker="o", color="darkorange")
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("Silhouette score")
    axes[1].set_title("Silhouette Analysis")
    plt.tight_layout()
    plt.savefig("k_selection.png")
    plt.close()

    best_k = list(k_range)[int(np.argmax(silhouettes))]
    return best_k, dict(zip(k_range, silhouettes))


def name_cluster(row, overall):
    """Turn a cluster's mean feature profile into a human-readable label."""
    income_tag = "high income" if row["Annual Income (k$)"] > overall["Annual Income (k$)"] else "low income"
    spend_tag = "high spender" if row["Spending Score (1-100)"] > overall["Spending Score (1-100)"] else "low spender"
    age_tag = "younger" if row["Age"] < overall["Age"] else "older"
    return f"{age_tag}, {income_tag}, {spend_tag}"


def main():
    df = load_data()
    X_raw = df[FEATURES]
    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    best_k, silhouette_by_k = choose_k(X)
    print("Silhouette scores by k:", {k: round(v, 3) for k, v in silhouette_by_k.items()})
    print("Selected k =", best_k)

    model = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    df["cluster"] = model.fit_predict(X)

    profile = df.groupby("cluster")[FEATURES].mean().round(2)
    overall = df[FEATURES].mean()
    profile["segment_name"] = profile.apply(lambda r: name_cluster(r, overall), axis=1)
    print("\nCluster profiles:\n", profile)

    # PCA visualization
    coords = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(X)
    plt.figure(figsize=(6, 5))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=df["cluster"], cmap="tab10", s=25)
    plt.title(f"Customer segments (PCA projection, k={best_k})")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend(*scatter.legend_elements(), title="Cluster", loc="best")
    plt.tight_layout()
    plt.savefig("clusters_pca.png")
    plt.close()

    df.to_csv("segmented_customers.csv", index=False)
    profile.to_csv("cluster_profiles.csv")
    joblib.dump({"scaler": scaler, "model": model, "features": FEATURES}, "segmentation_model.joblib", compress=3)

    with open("cluster_names.json", "w") as f:
        json.dump(profile["segment_name"].to_dict(), f, indent=2)

    print("\nSaved: segmentation_model.joblib, segmented_customers.csv, cluster_profiles.csv,")
    print("       k_selection.png, clusters_pca.png, cluster_names.json")


if __name__ == "__main__":
    main()
