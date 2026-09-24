import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from scipy.stats import ks_2samp

def fidelity(real, synthetic):
    """Per-column KS-test similarity (1 = identical distribution)."""
    scores = {}
    for col in real.columns:
        if real[col].dtype.kind in "fi":
            stat, _ = ks_2samp(real[col], synthetic[col])
            scores[col] = 1 - stat
    return scores

def utility_tstr(real_df, synth_df, target_col="target", test_size=0.3, seed=42):
    """Train-on-Synthetic, Test-on-Real utility score."""
    real_train, real_test = train_test_split(real_df, test_size=test_size, random_state=seed)
    X_s, y_s = synth_df.drop(columns=[target_col]), synth_df[target_col].round().astype(int)
    X_t, y_t = real_test.drop(columns=[target_col]), real_test[target_col]
    clf = RandomForestClassifier(random_state=seed).fit(X_s, y_s)
    pred = clf.predict(X_t)
    return accuracy_score(y_t, pred)

def utility_trtr(real_df, target_col="target", test_size=0.3, seed=42):
    """Train-on-Real, Test-on-Real baseline, for comparison against TSTR."""
    real_train, real_test = train_test_split(real_df, test_size=test_size, random_state=seed)
    X_tr, y_tr = real_train.drop(columns=[target_col]), real_train[target_col]
    X_te, y_te = real_test.drop(columns=[target_col]), real_test[target_col]
    clf = RandomForestClassifier(random_state=seed).fit(X_tr, y_tr)
    pred = clf.predict(X_te)
    return accuracy_score(y_te, pred)

def privacy_dcr(real_df, synth_df):
    """Mean distance from each synthetic row to its closest real
    neighbour -- higher means the generator is less likely to be
    memorizing/leaking real records."""
    from sklearn.metrics import pairwise_distances
    d = pairwise_distances(synth_df.values, real_df.values).min(axis=1).mean()
    return float(d)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--real_csv", default="data/real.csv")
    p.add_argument("--synth_csv", default="data/synthetic.csv")
    p.add_argument("--target_col", default="target")
    args = p.parse_args()

    real = pd.read_csv(args.real_csv)
    synth = pd.read_csv(args.synth_csv)

    print("Fidelity (per-column, 1.0 = identical):")
    for col, score in fidelity(real, synth).items():
        print(f"  {col}: {score:.3f}")

    trtr = utility_trtr(real, args.target_col)
    tstr = utility_tstr(real, synth, args.target_col)
    print(f"Utility TRTR (real baseline): {trtr:.3f}")
    print(f"Utility TSTR (synthetic):     {tstr:.3f}")

    dcr = privacy_dcr(real.drop(columns=[args.target_col]), synth.drop(columns=[args.target_col]))
    print(f"Privacy (mean distance to closest real record): {dcr:.3f}")
