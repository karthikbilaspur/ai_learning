"""Diagnostics for reward-model failure modes such as length bias."""
import numpy as np

def length_bias(rewards,lengths):
    rewards=np.asarray(rewards);lengths=np.asarray(lengths)
    return float(np.corrcoef(rewards,lengths)[0,1]) if len(rewards)>1 else 0.0

def chosen_margin(chosen,rejected):
    return float(np.mean(np.asarray(chosen)-np.asarray(rejected)))
