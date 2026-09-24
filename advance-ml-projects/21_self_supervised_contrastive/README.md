# 21 Self Supervised Contrastive -- Level 1

Self-Supervised Contrastive Learning (SimCLR) on CIFAR-10.

## What's here
- `src/config.py` - all hyperparameters in one place, overridable via CLI
- `src/model.py` - SimCLR with a CIFAR-sized ResNet-18 stem (3x3 conv,
  no maxpool) instead of the original 224px-tuned ResNet-50 stem
- `src/loss.py` - NT-Xent loss (+ a DINO loss, unused by the main pipeline)
- `src/train.py` - trains SimCLR, saves a checkpoint every epoch, supports `--resume`
- `src/eval_linear.py` - freezes the backbone and trains a linear
  classifier on top of it to report real test accuracy

## Run
```bash
pip install -r ../requirements.txt
python src/train.py --epochs 20 --subset 0        # --subset N for a quick smoke test
python src/eval_linear.py --checkpoint checkpoints/simclr_last.pt
```
