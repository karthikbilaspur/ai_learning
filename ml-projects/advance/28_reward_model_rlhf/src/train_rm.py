"""Trains the reward model with Bradley-Terry preference loss, a
train/val split, and pairwise accuracy (fraction of pairs where
reward(chosen) > reward(rejected)) reported each epoch. Runs on CPU or
GPU (previously the code hard-called .cuda(), which crashes on any
machine without a GPU).

    python train_rm.py --jsonl data/preferences.jsonl --base distilgpt2
"""
import argparse, os
import torch, torch.nn.functional as F
from transformers import AutoTokenizer
from dataset import PreferenceDataset, collate_fn
from reward_model import RewardModel
from torch.utils.data import DataLoader, random_split

def evaluate(model, loader, device):
    model.eval()
    correct = total = 0
    val_loss = 0.0
    with torch.no_grad():
        for chosen, rejected in loader:
            chosen = {k: v.to(device) for k, v in chosen.items()}
            rejected = {k: v.to(device) for k, v in rejected.items()}
            r_c = model(**chosen)
            r_r = model(**rejected)
            val_loss += (-F.logsigmoid(r_c - r_r)).sum().item()
            correct += (r_c > r_r).sum().item()
            total += r_c.size(0)
    return val_loss / max(total, 1), correct / max(total, 1)

def train_rm(jsonl_path="data/preferences.jsonl", base="distilgpt2",
             epochs=3, batch_size=8, lr=1e-5, val_frac=0.1,
             checkpoint_path="checkpoints/reward_model.pt"):
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    tokenizer = AutoTokenizer.from_pretrained(base)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    ds = PreferenceDataset(jsonl_path)
    n_val = max(1, int(len(ds) * val_frac))
    train_ds, val_ds = random_split(ds, [len(ds) - n_val, n_val],
                                     generator=torch.Generator().manual_seed(42))
    collate = lambda b: collate_fn(b, tokenizer)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=batch_size, collate_fn=collate)

    model = RewardModel(base).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    best_val_acc = -1
    for epoch in range(epochs):
        model.train()
        for chosen, rejected in train_loader:
            chosen = {k: v.to(device) for k, v in chosen.items()}
            rejected = {k: v.to(device) for k, v in rejected.items()}
            r_c = model(**chosen)
            r_r = model(**rejected)
            loss = -F.logsigmoid(r_c - r_r).mean()  # Bradley-Terry
            opt.zero_grad(); loss.backward(); opt.step()

        val_loss, val_acc = evaluate(model, val_loader, device)
        print(f"Epoch {epoch} val_loss={val_loss:.4f} val_pairwise_acc={val_acc:.4f}")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({"state_dict": model.state_dict(), "base": base,
                        "val_pairwise_acc": val_acc}, checkpoint_path)

    print(f"Best val_pairwise_acc={best_val_acc:.4f} -> saved {checkpoint_path}")
    return checkpoint_path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl", default="data/preferences.jsonl")
    p.add_argument("--base", default="distilgpt2")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch_size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--checkpoint_path", default="checkpoints/reward_model.pt")
    args = p.parse_args()
    train_rm(args.jsonl, args.base, args.epochs, args.batch_size, args.lr,
              checkpoint_path=args.checkpoint_path)
