"""Generates a synthetic-but-structured time series (seasonal + trend +
noise, like retail/energy demand) so the retrieval-augmented forecaster
has real repeating patterns to retrieve and learn from.

    python make_data.py --length 5000
"""
import argparse
import numpy as np

def generate(length=5000, seed=42):
    rng = np.random.default_rng(seed)
    t = np.arange(length)
    trend = 0.001 * t
    weekly = 3 * np.sin(2 * np.pi * t / 7)
    daily = 1.5 * np.sin(2 * np.pi * t / 1)
    noise = rng.normal(0, 0.5, size=length)
    series = 10 + trend + weekly + daily + noise
    return series.astype("float32")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--length", type=int, default=5000)
    p.add_argument("--out", default="data/series.npy")
    args = p.parse_args()
    series = generate(args.length)
    np.save(args.out, series)
    print(f"Wrote series of length {len(series)} to {args.out}")
