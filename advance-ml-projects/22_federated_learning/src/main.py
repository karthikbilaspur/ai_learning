"""End-to-end federated-learning simulation (no need to hand-launch a
server + N client processes -- uses Flower's in-process simulation runner).

    python main.py --num_clients 5 --num_rounds 10 --iid

Includes a --dp flag to switch on the DP-FedAvg strategy from strategy.py.
"""
import argparse
import flwr as fl
from flwr.common import ndarrays_to_parameters

from dataset import load_partitions
from client import FlowerClient, test
from model import Net
from strategy import DPFedAvg
from flwr.server.strategy import FedAvg


def make_client_fn(client_loaders):
    def client_fn(cid: str):
        train_loader, val_loader = client_loaders[int(cid)]
        return FlowerClient(train_loader, val_loader).to_client()
    return client_fn


def make_evaluate_fn(test_loader):
    def evaluate(server_round, parameters, config):
        model = Net()
        params_dict = zip(model.state_dict().keys(), parameters)
        import torch
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        model.load_state_dict(state_dict, strict=True)
        loss, acc = test(model, test_loader)
        print(f"[server round {server_round}] central test_acc={acc:.4f}")
        return loss, {"accuracy": acc}
    return evaluate


def main(args):
    client_loaders, test_loader = load_partitions(
        num_clients=args.num_clients, batch_size=args.batch_size, iid=args.iid)

    initial_params = ndarrays_to_parameters(
        [val.cpu().numpy() for _, val in Net().state_dict().items()])

    strategy_cls = DPFedAvg if args.dp else FedAvg
    extra = {"clip_norm": args.clip_norm, "noise_multiplier": args.noise_multiplier} if args.dp else {}
    strategy = strategy_cls(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=args.num_clients,
        min_evaluate_clients=args.num_clients,
        min_available_clients=args.num_clients,
        on_fit_config_fn=lambda rnd: {"lr": args.lr, "local_epochs": args.local_epochs},
        initial_parameters=initial_params,
        evaluate_fn=make_evaluate_fn(test_loader),
        **extra,
    )

    fl.simulation.start_simulation(
        client_fn=make_client_fn(client_loaders),
        num_clients=args.num_clients,
        config=fl.server.ServerConfig(num_rounds=args.num_rounds),
        strategy=strategy,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--num_clients", type=int, default=5)
    p.add_argument("--num_rounds", type=int, default=10)
    p.add_argument("--local_epochs", type=int, default=1)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--iid", action="store_true", default=True)
    p.add_argument("--dp", action="store_true", help="use differentially-private FedAvg")
    p.add_argument("--clip_norm", type=float, default=1.0)
    p.add_argument("--noise_multiplier", type=float, default=0.1)
    main(p.parse_args())
