import torch.nn as nn
SEARCH_SPACE={"hidden":[64,128,256,512],"layers":(1,4),"dropout":(0.0,0.5),"lr":(1e-4,1e-2)}
def build_model(hidden,layers,dropout,in_dim=784,out_dim=10):
    modules=[]; d=in_dim
    for _ in range(layers): modules += [nn.Linear(d,hidden),nn.ReLU(),nn.Dropout(dropout)]; d=hidden
    modules.append(nn.Linear(d,out_dim)); return nn.Sequential(*modules)

def parameter_count(model): return sum(p.numel() for p in model.parameters())
