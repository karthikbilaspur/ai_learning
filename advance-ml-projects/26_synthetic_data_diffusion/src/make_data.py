"""Generates a small synthetic tabular 'real' dataset (via sklearn) to
train/evaluate the diffusion model against, since none was included.

    python make_data.py --n_samples 3000
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

def generate(n_samples=3000, n_features=9, seed=42):
    X, y = make_classification(n_samples=n_samples, n_features=n_features,
                                n_informative=6, n_redundant=2, random_state=seed)
    cols = [f"f{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=cols)
    df["target"] = y
    return df

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n_samples", type=int, default=3000)
    p.add_argument("--n_features", type=int, default=9)
    p.add_argument("--out", default="data/real.csv")
    args = p.parse_args()
    df = generate(args.n_samples, args.n_features)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")
