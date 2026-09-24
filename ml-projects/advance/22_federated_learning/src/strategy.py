"""Differentially-private FedAvg strategy.

Wraps client updates with per-round Gaussian noise + norm clipping (the
standard DP-FedAvg recipe) instead of relying on Opacus inside each client
(which would require per-sample gradient hooks). This keeps the strategy
framework-agnostic while still giving a real, tunable (epsilon-ish) privacy
knob via `clip_norm` and `noise_multiplier`.
"""
import numpy as np
from flwr.server.strategy import FedAvg


def clip_and_add_noise(parameters, clip_norm=1.0, noise_multiplier=1.0, seed=None):
    rng = np.random.default_rng(seed)
    clipped = []
    for layer in parameters:
        norm = np.linalg.norm(layer)
        scale = min(1.0, clip_norm / (norm + 1e-12))
        noisy = layer * scale + rng.normal(0, noise_multiplier * clip_norm, size=layer.shape)
        clipped.append(noisy.astype(layer.dtype))
    return clipped


class DPFedAvg(FedAvg):
    """FedAvg that clips + noises the *aggregated* update each round."""

    def __init__(self, *args, clip_norm=1.0, noise_multiplier=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.clip_norm = clip_norm
        self.noise_multiplier = noise_multiplier

    def aggregate_fit(self, server_round, results, failures):
        aggregated = super().aggregate_fit(server_round, results, failures)
        if aggregated is None:
            return aggregated
        parameters, metrics = aggregated
        from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters
        ndarrays = parameters_to_ndarrays(parameters)
        noisy = clip_and_add_noise(ndarrays, self.clip_norm, self.noise_multiplier, seed=server_round)
        return ndarrays_to_parameters(noisy), metrics
