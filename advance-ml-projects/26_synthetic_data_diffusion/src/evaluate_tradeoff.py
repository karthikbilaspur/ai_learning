import argparse,json,pandas as pd
from evaluate_synthetic import fidelity,utility_tstr,utility_trtr,privacy_dcr

def evaluate(real,synth,target='target'):
    f=fidelity(real,synth); trtr=utility_trtr(real,target); tstr=utility_tstr(real,synth,target)
    dcr=privacy_dcr(real.drop(columns=[target]),synth.drop(columns=[target]))
    return {'mean_fidelity':sum(f.values())/max(1,len(f)),'trtr':trtr,'tstr':tstr,'tstr_retention':tstr/max(trtr,1e-8),'mean_dcr':dcr}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--real_csv',default='data/real.csv');p.add_argument('--synth_csv',default='data/synthetic.csv');p.add_argument('--target',default='target');a=p.parse_args();print(json.dumps(evaluate(pd.read_csv(a.real_csv),pd.read_csv(a.synth_csv),a.target),indent=2))
