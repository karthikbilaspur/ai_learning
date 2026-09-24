import torch, torch.nn as nn
import torchvision.models as models

class ProjectionHead(nn.Module):
    def __init__(self, in_dim=2048, hidden=512, out=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, out)
        )
    def forward(self, x): return self.net(x)

_BACKBONE_OUT_DIM = {
    "resnet18": 512,
    "resnet34": 512,
    "resnet50": 2048,
}

class SimCLR(nn.Module):
    def __init__(self, feature_dim=128, backbone="resnet18"):
        super().__init__()
        if backbone not in _BACKBONE_OUT_DIM:
            raise ValueError(f"Unknown backbone {backbone}, choose from {list(_BACKBONE_OUT_DIM)}")
        resnet_fn = getattr(models, backbone)
        resnet = resnet_fn(weights=None)
        # Swap the stem for small (32x32) images: 7x7/stride2 conv + maxpool throws away
        # too much spatial info on CIFAR-sized inputs.
        resnet.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        resnet.maxpool = nn.Identity()
        out_dim = _BACKBONE_OUT_DIM[backbone]
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.projection = ProjectionHead(out_dim, 512, feature_dim)
    def forward(self, x):
        h = self.backbone(x).flatten(start_dim=1)
        z = self.projection(h)
        return torch.nn.functional.normalize(z, dim=1)

class DINOHead(nn.Module):
    def __init__(self, in_dim=2048, out_dim=65536):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, 2048), nn.GELU(),
            nn.Linear(2048, 2048), nn.GELU(),
            nn.Linear(2048, out_dim)
        )
    def forward(self, x): return self.mlp(x)
