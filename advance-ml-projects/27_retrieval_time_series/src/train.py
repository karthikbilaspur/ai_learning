"""Trains the retrieval-augmented forecaster with a proper chronological
train/test split (previously there was no split and no eval metric beyond
training loss -- and the retriever, if reused at test time, would need to
avoid retrieving the test window itself).

    python train.py --series_path data/series.npy --epochs 30
"""
import argparse, os
import torch, numpy as np
from retriever import TimeSeriesRetriever
from forecaster import RAFTForecaster

def make_windows(series, window=96, pred=24):
    X, Y = [], []
    for i in range(len(series) - window - pred):
        X.append(series[i:i + window])
        Y.append(series[i + window:i + window + pred])
    return np.array(X), np.array(Y)

def train(series_path="data/series.npy", window=96, pred=24, k=5,
          epochs=30, batch_size=64, lr=1e-3, test_frac=0.15,
          checkpoint_path="checkpoints/raft.pt"):
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    series = np.load(series_path)
    X, Y = make_windows(series, window, pred)

    n = len(X)
    n_test = int(n * test_frac)
    split = n - n_test
    X_train, Y_train = X[:split], Y[:split]
    X_test, Y_test = X[split:], Y[split:]

    # Retrieval corpus = training windows only. The test windows are
    # never in the corpus, so no exclude_idx bookkeeping is needed there.
    retriever = TimeSeriesRetriever(X_train)
    model = RAFTForecaster(input_len=window, pred_len=pred, k_retrieved=k)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        perm = np.random.permutation(len(X_train))
        epoch_loss = 0.0
        for i in range(0, len(X_train), batch_size):
            batch_idx = perm[i:i + batch_size]
            xb = torch.tensor(X_train[batch_idx], dtype=torch.float32)
            yb = torch.tensor(Y_train[batch_idx], dtype=torch.float32)
            # Query windows come from the same corpus they retrieve from,
            # so each one must exclude *itself* -- otherwise the model
            # could trivially "retrieve its own answer".
            ret = np.array([retriever.retrieve(X_train[j], k=k, exclude_idx=j)[0]
                             for j in batch_idx])
            ret_tensor = torch.tensor(ret, dtype=torch.float32)
            pred_y = model(xb, ret_tensor)
            loss = torch.nn.functional.mse_loss(pred_y, yb)
            opt.zero_grad(); loss.backward(); opt.step()
            epoch_loss += loss.item() * len(batch_idx)
        print(f"Epoch {epoch} train_mse={epoch_loss/len(X_train):.4f}")

    # Evaluation on the held-out chronological test split.
    model.eval()
    with torch.no_grad():
        xb = torch.tensor(X_test, dtype=torch.float32)
        yb = torch.tensor(Y_test, dtype=torch.float32)
        # Test windows are never in the train-only corpus, so no
        # exclusion is needed here.
        ret = np.array([retriever.retrieve(q, k=k)[0] for q in X_test])
        ret_tensor = torch.tensor(ret, dtype=torch.float32)
        pred_y = model(xb, ret_tensor)
        mse = torch.nn.functional.mse_loss(pred_y, yb).item()
        mae = torch.nn.functional.l1_loss(pred_y, yb).item()
    print(f"TEST mse={mse:.4f} mae={mae:.4f}")

    torch.save({"state_dict": model.state_dict(), "window": window, "pred": pred,
                "k": k, "test_mse": mse, "test_mae": mae}, checkpoint_path)
    print(f"Saved checkpoint to {checkpoint_path}")
    return mse, mae

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--series_path", default="data/series.npy")
    p.add_argument("--window", type=int, default=96)
    p.add_argument("--pred", type=int, default=24)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch_size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--checkpoint_path", default="checkpoints/raft.pt")
    args = p.parse_args()
    train(args.series_path, args.window, args.pred, args.k, args.epochs,
          args.batch_size, args.lr, checkpoint_path=args.checkpoint_path)
