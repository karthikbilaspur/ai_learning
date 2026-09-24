"""Linear-probe evaluation of a trained SimCLR backbone.
Freezes the backbone, trains a single linear layer on top of it for
classification, and reports test accuracy -- the standard way to judge
whether self-supervised features are useful.
"""
import argparse
import torch, torch.nn as nn
import torchvision.transforms as T
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10

from config import Config
from model import SimCLR

def build_backbone(ckpt_path, backbone, feature_dim, device):
    model = SimCLR(feature_dim, backbone=backbone).to(device)
    ckpt = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    for p in model.parameters():
        p.requires_grad = False
    return model

@torch.no_grad()
def embed(model, x):
    h = model.backbone(x).flatten(start_dim=1)
    return h

def evaluate(cfg: Config, epochs=10, lr=1e-3):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tfm = T.Compose([T.ToTensor()])
    train_ds = CIFAR10(root=cfg.data_root, train=True, download=True, transform=tfm)
    test_ds = CIFAR10(root=cfg.data_root, train=False, download=True, transform=tfm)
    if cfg.subset:
        train_ds = torch.utils.data.Subset(train_ds, range(min(cfg.subset, len(train_ds))))
        test_ds = torch.utils.data.Subset(test_ds, range(min(cfg.subset // 5 or 1, len(test_ds))))
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False)

    backbone = build_backbone(cfg.resume or f"{cfg.checkpoint_dir}/simclr_last.pt",
                               cfg.backbone, cfg.feature_dim, device)
    out_dim = {"resnet18": 512, "resnet34": 512, "resnet50": 2048}[cfg.backbone]
    classifier = nn.Linear(out_dim, 10).to(device)
    opt = torch.optim.Adam(classifier.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        classifier.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            h = embed(backbone, x)
            logits = classifier(h)
            loss = criterion(logits, y)
            opt.zero_grad(); loss.backward(); opt.step()

        classifier.eval(); correct = total = 0
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)
                logits = classifier(embed(backbone, x))
                correct += (logits.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / max(total, 1)
        print(f"[linear-probe] epoch {epoch} test_acc={acc:.4f}")
    return acc

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default="./checkpoints/simclr_last.pt")
    p.add_argument("--backbone", default="resnet18")
    p.add_argument("--feature_dim", type=int, default=128)
    p.add_argument("--subset", type=int, default=0)
    args = p.parse_args()
    cfg = Config(resume=args.checkpoint, backbone=args.backbone,
                 feature_dim=args.feature_dim, subset=args.subset)
    evaluate(cfg)
