# 26 Synthetic Data Diffusion -- Level 1

Synthetic tabular data generation with a diffusion model (TabDDPM).

## What's here
- `src/make_data.py` - generates a synthetic "real" tabular dataset via
  `sklearn.make_classification` (none was included)
- `src/diffusion_tabular.py` - `DiffusionSchedule` now provides **one**
  consistent noise schedule shared by `q_sample` (training) and
  `p_sample_loop` (sampling) -- previously these used two different,
  incompatible schedules
- `src/train.py` - **new**: trains TabDDPM with the standard denoising
  objective and saves a checkpoint (previously there was no training
  script at all, and `generate.py` sampled from random-init weights)
- `src/generate.py` - now actually loads the trained checkpoint
- `src/evaluate_synthetic.py` - fidelity (KS-test), utility (TSTR vs a
  TRTR baseline), and privacy (distance-to-closest-record) metrics, with
  a CLI

## Run
```bash
pip install -r ../requirements.txt
python src/make_data.py --n_samples 3000
python src/train.py --csv data/real.csv --epochs 100
python src/generate.py --n_samples 1000
python src/evaluate_synthetic.py --real_csv data/real.csv --synth_csv data/synthetic.csv
```
