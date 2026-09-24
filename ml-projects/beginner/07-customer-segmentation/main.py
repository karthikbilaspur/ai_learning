import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

print("Customer Segmentation - K-Means")

np.random.seed(42)
df = pd.DataFrame({
    'Age': np.random.randint(18,70,200),
    'Annual Income (k$)': np.random.randint(15,150,200),
    'Spending Score (1-100)': np.random.randint(1,100,200)
})

X = df[['Annual Income (k$)','Spending Score (1-100)']]
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X)

print(df.head(10))
print(f"\nCluster centers:\n{kmeans.cluster_centers_}")

plt.figure(figsize=(8,6))
for c in range(5):
    cluster_data = df[df['Cluster']==c]
    plt.scatter(cluster_data['Annual Income (k$)'], cluster_data['Spending Score (1-100)'], label=f'Cluster {c}')
plt.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], s=200, c='black', marker='X', label='Centroids')
plt.xlabel('Annual Income')
plt.ylabel('Spending Score')
plt.legend()
plt.title('Customer Segments')
plt.savefig('clusters.png')
print("Saved clusters.png - shows 5 customer types")
