import pandas as pd, numpy as np, torch
from torch_geometric.data import Data

def build_graph(csv_path="data/transactions.csv", val_frac=0.15, test_frac=0.15, seed=42):
    """Builds one big transaction graph: each transaction is a node, and
    consecutive transactions by the same user are connected by an edge
    (a simple temporal user-activity graph). Node features are
    standardized. Returns a single PyG `Data` object with train/val/test
    boolean masks so the model can be trained and evaluated on disjoint
    transactions.
    """
    df = pd.read_csv(csv_path)
    feat_cols = ["amount", "time", "is_international"]
    x_raw = df[feat_cols].values.astype("float32")
    mean, std = x_raw.mean(axis=0), x_raw.std(axis=0) + 1e-8
    x = torch.tensor((x_raw - mean) / std, dtype=torch.float)

    edge_list = []
    for _, indices in df.groupby("user_id").indices.items():
        idx = list(indices)
        for i in range(len(idx) - 1):
            edge_list.append([idx[i], idx[i + 1]])
            edge_list.append([idx[i + 1], idx[i]])  # make it undirected
    edge_index = (torch.tensor(edge_list, dtype=torch.long).t().contiguous()
                  if edge_list else torch.empty((2, 0), dtype=torch.long))

    y = torch.tensor(df["is_fraud"].values, dtype=torch.long)

    rng = np.random.default_rng(seed)
    n = len(df)
    perm = rng.permutation(n)
    n_val, n_test = int(n * val_frac), int(n * test_frac)
    val_idx, test_idx, train_idx = perm[:n_val], perm[n_val:n_val + n_test], perm[n_val + n_test:]

    def mask_from(idx):
        m = torch.zeros(n, dtype=torch.bool); m[idx] = True; return m

    data = Data(x=x, edge_index=edge_index, y=y)
    data.train_mask = mask_from(train_idx)
    data.val_mask = mask_from(val_idx)
    data.test_mask = mask_from(test_idx)
    return data
