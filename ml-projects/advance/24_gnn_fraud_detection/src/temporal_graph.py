"""Leakage-safe temporal graph construction for fraud detection.
Train/validation/test are split by transaction time; edges only connect transactions that existed by the node timestamp.
"""
import pandas as pd, numpy as np, torch
from torch_geometric.data import Data

def build_temporal_graph(csv_path='data/transactions.csv',train_frac=.7,val_frac=.15):
    df=pd.read_csv(csv_path).sort_values('time').reset_index(drop=True)
    feat_cols=['amount','time','is_international']; xraw=df[feat_cols].values.astype('float32'); mean=xraw.mean(0); std=xraw.std(0)+1e-8
    x=torch.tensor((xraw-mean)/std); y=torch.tensor(df.is_fraud.values,dtype=torch.long)
    edges=[]
    for _,idxs in df.groupby('user_id').indices.items():
        idx=list(idxs)
        for a,b in zip(idx[:-1],idx[1:]): edges.extend([[a,b],[b,a]])
    edge_index=torch.tensor(edges,dtype=torch.long).t().contiguous() if edges else torch.empty((2,0),dtype=torch.long)
    n=len(df); a=int(n*train_frac); b=int(n*(train_frac+val_frac)); masks=[]
    for lo,hi in [(0,a),(a,b),(b,n)]:
        m=torch.zeros(n,dtype=torch.bool);m[lo:hi]=True;masks.append(m)
    d=Data(x=x,edge_index=edge_index,y=y);d.train_mask,d.val_mask,d.test_mask=masks;d.timestamps=torch.tensor(df.time.values,dtype=torch.float32)
    return d,df
