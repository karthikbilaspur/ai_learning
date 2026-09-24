"""Central config for the SimCLR self-supervised pipeline.
Override any value from the CLI, e.g. `python train.py --epochs 5 --subset 2000`.
"""
from dataclasses import dataclass

@dataclass
class Config:
    data_root: str = "./data"
    checkpoint_dir: str = "./checkpoints"
    backbone: str = "resnet18"       # resnet18 is lighter than resnet50 and fits CIFAR-32 better
    feature_dim: int = 128
    batch_size: int = 256
    epochs: int = 20
    lr: float = 3e-4
    weight_decay: float = 1e-6
    temperature: float = 0.5
    num_workers: int = 4
    subset: int = 0                  # 0 = full dataset; >0 = quick smoke-test on a slice
    seed: int = 42
    resume: str = ""                 # path to a checkpoint to resume from
