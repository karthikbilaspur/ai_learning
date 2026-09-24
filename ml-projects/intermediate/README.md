# ML Projects 11-20 — Level 2 Upgrade Pack

Level 2 upgrades of all 10 projects from the original pack. Each project
folder is self-contained: `train.py` trains and evaluates the model(s),
`app.py` launches an interactive Gradio demo, and the folder's own
`README.md` documents exactly what changed from Level 1, the results
obtained, and honest limitations.

## What's genuinely new across the pack

**Real public datasets** (pulled in for 4 of the 10 projects — network
access in the build environment limited how many could be sourced):
| Project | Dataset |
|---|---|
| 11 Customer Segmentation | Mall Customers (200 shoppers) |
| 13 Used Car Price Prediction | CarPrice_Assignment (205 US-market cars) |
| 16 Employee Attrition | IBM HR Analytics Attrition (1,470 employees) |
| 20 Movie Recommendation | IMDB movie metadata (5,043 movies) |

The other 6 projects (12, 14, 15, 17, 18, 19) use meaningfully upgraded
synthetic data (labeled ground truth, realistic correlations, harder
separability) since accessible real-data mirrors weren't reachable from
this environment's network allowlist. Each of those READMEs names the
specific real dataset to swap in next and confirms the rest of the
pipeline (CV, tuning, evaluation) needs no other changes to use it.

**Modeling upgrades, every project:**
- Cross-validation instead of a single train/test split (walk-forward CV
  for the time-series project).
- Multiple candidate models compared head-to-head, not one fixed algorithm.
- Hyperparameter tuning for the winning model where it mattered (13, 15).
- Proper metrics for the problem: PR-AUC for imbalanced classification
  (14, 16), MAPE for forecasting (17), per-class + cost-aware metrics for
  ordinal classification (19), genre-overlap sanity check for the
  recommender (20).
- SHAP explainability for the tree-based regressors/classifiers (13, 15, 16).
- Every project ships an interactive **Gradio demo** (`app.py`) — this is
  the actual "deployment" upgrade: a working interface instead of only a
  script that prints metrics to a terminal.

## Run any project
```bash
cd <project_folder>
pip install -r requirements.txt
python train.py      # trains, evaluates, saves the model + plots
python app.py         # launches the Gradio demo at http://localhost:7860
```

## Honest scorecard
Some results are genuinely strong (used car price R²≈0.955, air quality
R²≈0.968, movie genre-overlap 78.5%). Others are explicitly flagged as
not-yet-real (news classifier and fake-review detector are still
synthetic and score near-perfectly as a result; the demand forecast's
prediction interval isn't well-calibrated yet). Each project's own README
says which bucket it's in — that honesty is itself part of the Level 2
upgrade over the original pack, which reported metrics without noting
these caveats.
