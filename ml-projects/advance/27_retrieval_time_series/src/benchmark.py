"""Common forecasting metrics and a leakage-safe split contract."""
import numpy as np

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p);err=y-p
    return {'mae':float(np.mean(np.abs(err))),'rmse':float(np.sqrt(np.mean(err**2))),'smape':float(np.mean(2*np.abs(err)/(np.abs(y)+np.abs(p)+1e-8)))}

def temporal_split(series,train=.7,val=.15):
    n=len(series);a=int(n*train);b=int(n*(train+val));return series[:a],series[a:b],series[b:]
