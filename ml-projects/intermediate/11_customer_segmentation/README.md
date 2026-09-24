# 11 - Customer Segmentation (Level 2)

K-Means clustering on the real **Mall Customers** dataset (200 shoppers),
upgraded from the Level 1 synthetic-data demo.

## What changed from Level 1
- Real dataset (`data/Mall_Customers.csv`) instead of generated data.
- k chosen using **silhouette score** alongside the elbow plot (k=6 selected).
- PCA 2D projection of the clusters for visualization.
- Clusters are automatically labeled (e.g. "younger, high income, high spender")
  based on their feature profile, not just numbered.
- Interactive Gradio demo (`app.py`) that assigns a new customer to a segment.

## Run
```bash
pip install -r requirements.txt
python train.py      # trains, saves segmentation_model.joblib + plots
python app.py         # launches the interactive demo
```

## Outputs
`segmentation_model.joblib`, `segmented_customers.csv`, `cluster_profiles.csv`,
`cluster_names.json`, `k_selection.png` (elbow + silhouette), `clusters_pca.png`

## Level 3 ideas
Compare against GMM/DBSCAN; build a full dashboard where a user uploads their
own CSV and gets live segment assignments and profiles.
