"""Partitions CIFAR-10 into N client shards (IID or simple label-skew non-IID)."""
import torch
from torch.utils.data import DataLoader, Subset
import torchvision.transforms as T
from torchvision.datasets import CIFAR10
import numpy as np

def load_partitions(num_clients=5, data_root="./data", batch_size=32,
                     val_split=0.1, iid=True, seed=42):
    rng = np.random.default_rng(seed)
    tfm = T.Compose([T.ToTensor()])
    train_full = CIFAR10(root=data_root, train=True, download=True, transform=tfm)
    test_full = CIFAR10(root=data_root, train=False, download=True, transform=tfm)

    n = len(train_full)
    idx = np.arange(n)
    if iid:
        rng.shuffle(idx)
        shards = np.array_split(idx, num_clients)
    else:
        # simple label-skew: sort by label, then chunk -> each client sees few classes
        labels = np.array(train_full.targets)
        order = np.argsort(labels)
        shards = np.array_split(order, num_clients)

    client_loaders = []
    for shard in shards:
        rng.shuffle(shard)
        cut = int(len(shard) * (1 - val_split))
        train_idx, val_idx = shard[:cut], shard[cut:]
        train_loader = DataLoader(Subset(train_full, train_idx), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(Subset(train_full, val_idx), batch_size=batch_size, shuffle=False)
        client_loaders.append((train_loader, val_loader))

    test_loader = DataLoader(test_full, batch_size=256, shuffle=False)
    return client_loaders, test_loader
