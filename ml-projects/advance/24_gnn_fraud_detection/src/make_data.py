"""Generates a small synthetic credit-card-transaction dataset so the
project runs out-of-the-box with no external download.

    python make_data.py --n_users 200 --n_tx 5000

Produces data/transactions.csv with columns:
    user_id, amount, time, is_international, is_fraud
Fraud is injected as a minority class (~3%) with amount/time patterns
that are learnable (larger amounts, odd hours, international) so the
GNN has real signal to pick up, not just noise.
"""
import argparse
import numpy as np
import pandas as pd

def generate(n_users=200, n_tx=5000, fraud_rate=0.03, seed=42):
    rng = np.random.default_rng(seed)
    user_id = rng.integers(0, n_users, size=n_tx)
    time = np.sort(rng.uniform(0, 30 * 24, size=n_tx))  # hours over a 30-day window
    is_international = rng.binomial(1, 0.1, size=n_tx)
    amount = rng.lognormal(mean=3.0, sigma=1.0, size=n_tx)

    is_fraud = rng.binomial(1, fraud_rate, size=n_tx).astype(bool)
    # Make fraud rows look different: bigger amounts, more international, odd hours.
    amount[is_fraud] *= rng.uniform(3, 8, size=is_fraud.sum())
    is_international[is_fraud] = rng.binomial(1, 0.6, size=is_fraud.sum())
    hour_of_day = time % 24
    night_mask = is_fraud & (rng.random(n_tx) < 0.5)
    time[night_mask] = (time[night_mask] // 24) * 24 + rng.uniform(1, 4, size=night_mask.sum())

    df = pd.DataFrame({
        "user_id": user_id,
        "amount": amount,
        "time": time,
        "is_international": is_international,
        "is_fraud": is_fraud.astype(int),
    }).sort_values("time").reset_index(drop=True)
    return df

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n_users", type=int, default=200)
    p.add_argument("--n_tx", type=int, default=5000)
    p.add_argument("--fraud_rate", type=float, default=0.03)
    p.add_argument("--out", default="data/transactions.csv")
    args = p.parse_args()
    df = generate(args.n_users, args.n_tx, args.fraud_rate)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows ({df['is_fraud'].sum()} fraud) to {args.out}")
