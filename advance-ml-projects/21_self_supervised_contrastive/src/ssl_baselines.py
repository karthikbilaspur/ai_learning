"""Level-2 SSL baselines and ablation runner.
Implements SimSiam and a reusable evaluation table alongside SimCLR.
"""
import argparse, csv, os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.datasets import CIFAR10
from torchvision import transforms as T
from torch.utils.data import DataLoader
from model import SimCLR
from config import Config

class SimSiam(nn.Module):
    def __init__(self, backbone="resnet18", dim=2048, proj_dim=128):
        super().__init__()
        base = __import__('torchvision.models', fromlist=['']).__dict__[backbone](weights=None)
        base.conv1 = nn.Conv2d(3,64,3,1,1,bias=False); base.maxpool = nn.Identity()
        self.encoder = nn.Sequential(*list(base.children())[:-1])
        out = 512 if backbone in ("resnet18","resnet34") else 2048
        self.projector = nn.Sequential(nn.Linear(out, 512), nn.BatchNorm1d(512), nn.ReLU(), nn.Linear(512, proj_dim))
        self.predictor = nn.Sequential(nn.Linear(proj_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Linear(256, proj_dim))
    def encode(self,x): return self.encoder(x).flatten(1)
    def forward(self,x1,x2):
        z1=self.projector(self.encode(x1)); z2=self.projector(self.encode(x2))
        return self.predictor(z1), z2.detach(), self.predictor(z2), z1.detach()

def neg_cos(p,z): return -(F.normalize(p,dim=1)*F.normalize(z,dim=1)).sum(1).mean()

def run_ablation(output="results/ssl_ablation.csv", temperatures=(0.1,0.5,1.0), epochs=2, subset=5000):
    os.makedirs(os.path.dirname(output) or '.', exist_ok=True)
    rows=[]
    for t in temperatures:
        rows.append({"method":"SimCLR","temperature":t,"epochs":epochs,"subset":subset,"note":"Use train.py/eval_linear.py for full run"})
    with open(output,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(f"Wrote ablation plan to {output}. Train each configuration with --temperature and compare linear-probe accuracy.")

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',default='results/ssl_ablation.csv'); p.add_argument('--epochs',type=int,default=2); args=p.parse_args(); run_ablation(output=args.output,epochs=args.epochs)
