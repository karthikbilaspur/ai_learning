import argparse, os, random
import numpy as np
import torch, torchvision.transforms as T
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import CIFAR10

from config import Config
from model import SimCLR
from loss import NTXentLoss

transform = T.Compose([
    T.RandomResizedCrop(32),
    T.RandomHorizontalFlip(),
    T.ColorJitter(0.8, 0.8, 0.8, 0.2),
    T.RandomGrayscale(p=0.2),
    T.ToTensor(),
])

class SimCLRTransform:
    def __call__(self, x):
        return transform(x), transform(x)

def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

def build_dataloader(cfg: Config):
    dataset = CIFAR10(root=cfg.data_root, train=True, download=True, transform=SimCLRTransform())
    if cfg.subset:
        idx = list(range(min(cfg.subset, len(dataset))))
        dataset = Subset(dataset, idx)
    return DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True,
                       num_workers=cfg.num_workers, drop_last=True)

def train(cfg: Config):
    set_seed(cfg.seed)
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    loader = build_dataloader(cfg)
    model = SimCLR(cfg.feature_dim, backbone=cfg.backbone).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    criterion = NTXentLoss(temperature=cfg.temperature)

    start_epoch = 0
    if cfg.resume and os.path.exists(cfg.resume):
        ckpt = torch.load(cfg.resume, map_location=device)
        model.load_state_dict(ckpt["model"])
        opt.load_state_dict(ckpt["optimizer"])
        start_epoch = ckpt["epoch"] + 1
        print(f"Resumed from {cfg.resume} at epoch {start_epoch}")

    for epoch in range(start_epoch, cfg.epochs):
        model.train()
        running_loss, n_batches = 0.0, 0
        for (x_i, x_j), _ in loader:
            x_i, x_j = x_i.to(device), x_j.to(device)
            z_i, z_j = model(x_i), model(x_j)
            loss = criterion(z_i, z_j)
            opt.zero_grad(); loss.backward(); opt.step()
            running_loss += loss.item(); n_batches += 1
        avg_loss = running_loss / max(n_batches, 1)
        print(f"Epoch {epoch} avg_loss={avg_loss:.4f}")

        ckpt_path = os.path.join(cfg.checkpoint_dir, "simclr_last.pt")
        torch.save({"model": model.state_dict(), "optimizer": opt.state_dict(),
                    "epoch": epoch, "config": cfg.__dict__}, ckpt_path)
    print(f"Training complete. Final checkpoint: {ckpt_path}")
    return ckpt_path

def parse_args():
    cfg = Config()
    p = argparse.ArgumentParser(description="SimCLR self-supervised training")
    for field, default in cfg.__dict__.items():
        p.add_argument(f"--{field}", type=type(default), default=default)
    args = p.parse_args()
    return Config(**vars(args))

if __name__ == "__main__":
    train(parse_args())
