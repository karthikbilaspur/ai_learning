"""Trains the fraud-detection GNN and reports F1/AUC on held-out
transactions (previously it trained and "evaluated" on the same graph
with no split).

    python train.py --model gat --epochs 100
"""
import argparse, os
import torch
from graph_builder import build_graph
from gnn_model import FraudGAT, FraudGraphSAGE
from sklearn.metrics import f1_score, roc_auc_score

MODELS = {"gat": FraudGAT, "sage": FraudGraphSAGE}

def train(model_name="gat", epochs=100, lr=1e-3, weight_decay=5e-4,
          data_path="data/transactions.csv", checkpoint_dir="checkpoints"):
    os.makedirs(checkpoint_dir, exist_ok=True)
    data = build_graph(data_path)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    data = data.to(device)

    model_cls = MODELS[model_name]
    model = model_cls(in_dim=data.x.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    # class imbalance: upweight fraud in the loss, computed from the training split only
    n_pos = data.y[data.train_mask].sum().item()
    n_neg = data.train_mask.sum().item() - n_pos
    pos_weight = max(n_neg / max(n_pos, 1), 1.0)
    weight = torch.tensor([1.0, pos_weight], device=device)
    criterion = torch.nn.CrossEntropyLoss(weight=weight)

    best_val_f1, best_state = -1, None
    for epoch in range(epochs):
        model.train()
        opt.zero_grad()
        out = model(data)
        loss = criterion(out[data.train_mask], data.y[data.train_mask])
        loss.backward(); opt.step()

        if epoch % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                out = model(data)
                probs = torch.softmax(out, dim=1)[:, 1]
                pred = out.argmax(1)

                def metrics(mask):
                    y_true = data.y[mask].cpu().numpy()
                    y_pred = pred[mask].cpu().numpy()
                    y_prob = probs[mask].cpu().numpy()
                    f1 = f1_score(y_true, y_pred, zero_division=0)
                    try:
                        auc = roc_auc_score(y_true, y_prob)
                    except ValueError:
                        auc = float("nan")  # only one class present in split
                    return f1, auc

                train_f1, train_auc = metrics(data.train_mask)
                val_f1, val_auc = metrics(data.val_mask)
                print(f"Epoch {epoch} loss={loss.item():.4f} "
                      f"train_f1={train_f1:.3f} train_auc={train_auc:.3f} "
                      f"val_f1={val_f1:.3f} val_auc={val_auc:.3f}")
                if val_f1 > best_val_f1:
                    best_val_f1 = val_f1
                    best_state = {k: v.clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    torch.save({"state_dict": model.state_dict(), "model_name": model_name},
               os.path.join(checkpoint_dir, "best_model.pt"))

    model.eval()
    with torch.no_grad():
        out = model(data)
        probs = torch.softmax(out, dim=1)[:, 1]
        pred = out.argmax(1)
        y_true = data.y[data.test_mask].cpu().numpy()
        y_pred = pred[data.test_mask].cpu().numpy()
        y_prob = probs[data.test_mask].cpu().numpy()
        test_f1 = f1_score(y_true, y_pred, zero_division=0)
        try:
            test_auc = roc_auc_score(y_true, y_prob)
        except ValueError:
            test_auc = float("nan")
    print(f"TEST f1={test_f1:.4f} auc={test_auc:.4f}")
    return test_f1, test_auc

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=list(MODELS), default="gat")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--data_path", default="data/transactions.csv")
    p.add_argument("--checkpoint_dir", default="checkpoints")
    args = p.parse_args()
    train(args.model, args.epochs, args.lr, data_path=args.data_path,
          checkpoint_dir=args.checkpoint_dir)
