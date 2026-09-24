# 22 Federated Learning -- Level 1

Federated Learning for Privacy-Preserving ML across clients, with a real
differentially-private aggregation strategy.

## What's here
- `src/dataset.py` - partitions CIFAR-10 into N client shards (IID or label-skew non-IID)
- `src/strategy.py` - `DPFedAvg`: clips + adds Gaussian noise to the
  aggregated update each round (was an empty comment-only stub before)
- `src/client.py` / `src/server.py` - Flower client/server for a real
  multi-process deployment
- `src/main.py` - runs the whole thing in-process via Flower's simulation API

## Run
```bash
pip install -r ../requirements.txt
python src/main.py --num_clients 5 --num_rounds 10           # plain FedAvg
python src/main.py --num_clients 5 --num_rounds 10 --dp \
    --clip_norm 1.0 --noise_multiplier 0.1                    # DP-FedAvg
```
