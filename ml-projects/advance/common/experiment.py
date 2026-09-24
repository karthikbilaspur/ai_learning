"""Small, dependency-light experiment utilities shared by Level-2 projects."""
from __future__ import annotations
import json, os, random, time
from dataclasses import asdict, is_dataclass
from typing import Any
import numpy as np


def seed_everything(seed: int = 42) -> None:
    random.seed(seed); np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def save_json(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if is_dataclass(payload): payload = asdict(payload)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)


class Timer:
    def __enter__(self): self.start = time.perf_counter(); return self
    def __exit__(self, *args): self.elapsed = time.perf_counter() - self.start
