import torch, torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
import torchvision.transforms as T

def _loaders(data_root, batch_size=128):
    train = DataLoader(MNIST(data_root, train=True, download=True, transform=T.ToTensor()),
                        batch_size=batch_size, shuffle=True)
    val = DataLoader(MNIST(data_root, train=False, download=True, transform=T.ToTensor()),
                      batch_size=256)
    return train, val

def _run_epochs(model, loader, opt, device, epochs):
    model.train()
    for _ in range(epochs):
        for x, y in loader:
            x = x.view(x.size(0), -1).to(device); y = y.to(device)
            opt.zero_grad()
            loss = nn.CrossEntropyLoss()(model(x), y)
            loss.backward(); opt.step()

def _accuracy(model, loader, device):
    correct = total = 0
    model.eval()
    with torch.no_grad():
        for x, y in loader:
            x = x.view(x.size(0), -1).to(device); y = y.to(device)
            pred = model(x).argmax(1)
            correct += (pred == y).sum().item(); total += y.size(0)
    return correct / max(total, 1)

def evaluate(model, lr=1e-3, epochs=2, data_root="./data"):
    """Short train + val accuracy -- used as the Optuna search signal."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    train_loader, val_loader = _loaders(data_root)
    _run_epochs(model, train_loader, opt, device, epochs)
    return _accuracy(model, val_loader, device)

def train_full(model, lr=1e-3, epochs=10, data_root="./data"):
    """Longer retrain of the winning architecture -- used once after search."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    train_loader, val_loader = _loaders(data_root)
    _run_epochs(model, train_loader, opt, device, epochs)
    return _accuracy(model, val_loader, device)
