# 23 Neural Architecture Search -- Level 1

Neural Architecture Search / hyperparameter search over an MLP search
space on MNIST, via Optuna.

## What's here
- `src/search_space.py` - one search-space definition + model builder
  (previously this also imported NNI's search-space format, which was
  never actually used -- the real search ran through Optuna. Consolidated
  to a single backend.)
- `src/evaluator.py` - short-train-and-validate (search signal) and a
  longer full-train (for the final retrain)
- `src/controller.py` - runs the Optuna study, then retrains and saves
  the winning architecture to `checkpoints/best_model.pt`

## Run
```bash
pip install -r ../requirements.txt
python src/controller.py --n_trials 20 --epochs 3 --final_epochs 10
```
