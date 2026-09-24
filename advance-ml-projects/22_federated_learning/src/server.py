"""Standalone Flower server for a *real* multi-process deployment
(use this instead of main.py's simulation when clients run on separate
machines/processes). Start this first, then run client.py once per client
with `--server_address` pointing here and `--cid` set to its partition id.
"""
import argparse
import flwr as fl
from strategy import DPFedAvg
from flwr.server.strategy import FedAvg

def build_strategy(dp, clip_norm, noise_multiplier, num_clients):
    kwargs = dict(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=num_clients,
        min_evaluate_clients=num_clients,
        min_available_clients=num_clients,
        on_fit_config_fn=lambda rnd: {"lr": 0.01, "local_epochs": 1},
    )
    if dp:
        return DPFedAvg(clip_norm=clip_norm, noise_multiplier=noise_multiplier, **kwargs)
    return FedAvg(**kwargs)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--address", default="0.0.0.0:8080")
    p.add_argument("--num_rounds", type=int, default=10)
    p.add_argument("--num_clients", type=int, default=2)
    p.add_argument("--dp", action="store_true")
    p.add_argument("--clip_norm", type=float, default=1.0)
    p.add_argument("--noise_multiplier", type=float, default=0.1)
    args = p.parse_args()

    fl.server.start_server(
        server_address=args.address,
        config=fl.server.ServerConfig(num_rounds=args.num_rounds),
        strategy=build_strategy(args.dp, args.clip_norm, args.noise_multiplier, args.num_clients),
    )
