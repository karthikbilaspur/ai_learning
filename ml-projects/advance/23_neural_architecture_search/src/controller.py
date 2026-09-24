"""Optuna-driven architecture + hyperparameter search over the MLP
search space in search_space.py, on MNIST.

    python controller.py --n_trials 20 --epochs 3

After the study finishes, retrains the best config for longer and saves
it to checkpoints/best_model.pt.
"""
import argparse, os, json
import torch
import optuna

from search_space import SEARCH_SPACE, build_model
from evaluator import evaluate, train_full

def objective(trial, epochs, data_root):
    hidden = trial.suggest_categorical("hidden", SEARCH_SPACE["hidden"])
    layers = trial.suggest_int("layers", *SEARCH_SPACE["layers"])
    dropout = trial.suggest_float("dropout", *SEARCH_SPACE["dropout"])
    lr = trial.suggest_float("lr", *SEARCH_SPACE["lr"], log=True)
    model = build_model(hidden, layers, dropout)
    acc = evaluate(model, lr=lr, epochs=epochs, data_root=data_root)
    return acc

def run(n_trials=20, epochs=3, final_epochs=10, data_root="./data",
        checkpoint_dir="./checkpoints"):
    os.makedirs(checkpoint_dir, exist_ok=True)
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda t: objective(t, epochs, data_root), n_trials=n_trials)

    print("Best params:", study.best_params)
    print("Best val acc (short training):", study.best_value)

    with open(os.path.join(checkpoint_dir, "best_params.json"), "w") as f:
        json.dump(study.best_params, f, indent=2)

    # Retrain the winning architecture for longer and persist it.
    bp = study.best_params
    best_model = build_model(bp["hidden"], bp["layers"], bp["dropout"])
    final_acc = train_full(best_model, lr=bp["lr"], epochs=final_epochs, data_root=data_root)
    torch.save({"state_dict": best_model.state_dict(), "params": bp, "test_acc": final_acc},
               os.path.join(checkpoint_dir, "best_model.pt"))
    print(f"Final retrained test_acc={final_acc:.4f} -> saved best_model.pt")
    return study

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n_trials", type=int, default=20)
    p.add_argument("--epochs", type=int, default=3, help="epochs per trial during search")
    p.add_argument("--final_epochs", type=int, default=10, help="epochs for final retrain")
    p.add_argument("--data_root", default="./data")
    p.add_argument("--checkpoint_dir", default="./checkpoints")
    args = p.parse_args()
    run(args.n_trials, args.epochs, args.final_epochs, args.data_root, args.checkpoint_dir)
