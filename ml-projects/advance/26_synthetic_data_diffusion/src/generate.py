import argparse
import torch, pandas as pd
from diffusion_tabular import TabDDPM, DiffusionSchedule, p_sample_loop

def generate_synthetic(checkpoint_path="checkpoints/tabddpm.pt", n_samples=1000,
                        out_csv="data/synthetic.csv", sampling_steps=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ckpt = torch.load(checkpoint_path, map_location=device)
    feature_cols, mean, std, steps = (ckpt["feature_cols"], ckpt["mean"],
                                       ckpt["std"], ckpt["steps"])
    steps = sampling_steps or steps

    model = TabDDPM(input_dim=len(feature_cols)).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    schedule = DiffusionSchedule(steps=steps, device=device)
    synth_std = p_sample_loop(model, (n_samples, len(feature_cols)), schedule, device=device)
    synth = synth_std.cpu().numpy() * std + mean  # undo standardization

    synth_df = pd.DataFrame(synth, columns=feature_cols)
    synth_df.to_csv(out_csv, index=False)
    print(f"Saved {n_samples} synthetic rows to {out_csv}")
    return synth_df

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint_path", default="checkpoints/tabddpm.pt")
    p.add_argument("--n_samples", type=int, default=1000)
    p.add_argument("--out_csv", default="data/synthetic.csv")
    p.add_argument("--sampling_steps", type=int, default=None,
                    help="fewer steps = faster, lower-fidelity sampling")
    args = p.parse_args()
    generate_synthetic(args.checkpoint_path, args.n_samples, args.out_csv, args.sampling_steps)
