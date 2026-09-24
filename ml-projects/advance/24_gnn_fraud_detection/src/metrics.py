import numpy as np
from sklearn.metrics import f1_score,roc_auc_score,average_precision_score

def fraud_metrics(y,p):
    y=np.asarray(y); p=np.asarray(p); pred=(p>=.5).astype(int)
    return {'f1':float(f1_score(y,pred,zero_division=0)), 'roc_auc':float(roc_auc_score(y,p)) if len(np.unique(y))>1 else 0.0,
            'pr_auc':float(average_precision_score(y,p)) if len(np.unique(y))>1 else 0.0}
