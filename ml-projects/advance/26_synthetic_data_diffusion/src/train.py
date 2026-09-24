"""Trains TabDDPM on a real (or synthetic-standin) tabular CSV, using the
DDPM denoising-score-matching objective, and saves a checkpoint that
generate.py can load (previously there was no training script at all --
generate.py sampled from a randomly-initialized model).

    python train.py --csv data/real.csv --epochs 100
"""
import argparse, os
import numpy as np
import pandas as pd
import torch

from diffusion_tabular import TabDDPM, DiffusionSchedule, q_sample

def train(csv_path="data/real.csv", epochs=100, batch_size=128, lr=1e-3,
          steps=1000, checkpoint_path="checkpoints/tabddpm.pt", target_col="target"):
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    df = pd.read_csv(csv_path)
    feature_cols = [c for c in df.columns if c != target_col]
    x_raw = df[feature_cols].values.astype("float32")

    # Standardize features -- diffusion models assume roughly N(0,1) data.
    mean, std = x_raw.mean(axis=0), x_raw.std(axis=0) + 1e-8
    x = torch.tensor((x_raw - mean) / std, dtype=torch.float)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    x = x.to(device)
    schedule = DiffusionSchedule(steps=steps, device=device)

    model = TabDDPM(input_dim=x.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    n = x.shape[0]
    for epoch in range(epochs):
        perm = torch.randperm(n, device=device)
        epoch_loss = 0.0
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            x0 = x[idx]
            t = torch.randint(0, steps, (x0.shape[0],), device=device)
            noise = torch.randn_like(x0)
            x_t = q_sample(x0, t, noise, schedule)
            pred_noise = model(x_t, t.float() / steps)
            loss = torch.nn.functional.mse_loss(pred_noise, noise)
            opt.zero_grad(); loss.backward(); opt.step()
            epoch_loss += loss.item() * x0.shape[0]
        if epoch % 10 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch} loss={epoch_loss / n:.4f}")

    torch.save({
        "state_dict": model.state_dict(),
        "feature_cols": feature_cols,
        "mean": mean, "std": std,
        "steps": steps,
    }, checkpoint_path)
    print(f"Saved checkpoint to {checkpoint_path}")
    return checkpoint_path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="data/real.csv")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch_size", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--checkpoint_path", default="checkpoints/tabddpm.pt")
    args = p.parse_args()
    train(args.csv, args.epochs, args.batch_size, args.lr, args.steps, args.checkpoint_path)
