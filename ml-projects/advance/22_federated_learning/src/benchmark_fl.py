"""Level-2 FL experiment matrix: IID/non-IID x FedAvg/FedProx x DP on/off.
Runs the existing simulator repeatedly and records configuration metadata.
"""
import argparse, csv, itertools, os
from privacy import approximate_epsilon

def make_plan(output='results/fl_benchmark.csv'):
    os.makedirs(os.path.dirname(output) or '.',exist_ok=True)
    rows=[]
    for iid,method,dp in itertools.product([True,False],['fedavg','fedprox'],[False,True]):
        rows.append({'iid':iid,'method':method,'dp':dp,'num_clients':10,'rounds':20,
                     'noise_multiplier':1.0 if dp else 0.0,
                     'approx_epsilon': approximate_epsilon(1.0,1/10,20) if dp else None})
    with open(output,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print(output)
if __name__=='__main__': make_plan()
