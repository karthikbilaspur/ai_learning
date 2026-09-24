import torch, torch.nn as nn
class TransformerForecaster(nn.Module):
    def __init__(self,input_len=96,pred_len=24,d_model=128,nhead=4,layers=2):
        super().__init__();self.proj=nn.Linear(1,d_model);self.pos=nn.Parameter(torch.randn(1,input_len,d_model)*.02)
        enc=nn.TransformerEncoderLayer(d_model,nhead,batch_first=True);self.enc=nn.TransformerEncoder(enc,layers);self.head=nn.Sequential(nn.LayerNorm(d_model),nn.Linear(d_model,pred_len))
    def forward(self,x):
        h=self.proj(x.unsqueeze(-1))+self.pos[:,:x.size(1)];h=self.enc(h);return self.head(h[:,-1])
