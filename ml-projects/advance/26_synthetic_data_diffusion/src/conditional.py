"""Conditional tabular diffusion building block.
The condition vector is embedded and injected into the denoiser, enabling controlled generation."""
import torch, torch.nn as nn
class ConditionalDenoiser(nn.Module):
    def __init__(self,data_dim,cond_dim,hidden=256,timesteps=1000):
        super().__init__(); self.time=nn.Embedding(timesteps,hidden); self.cond=nn.Sequential(nn.Linear(cond_dim,hidden),nn.SiLU())
        self.net=nn.Sequential(nn.Linear(data_dim+hidden*2,hidden),nn.SiLU(),nn.Linear(hidden,hidden),nn.SiLU(),nn.Linear(hidden,data_dim))
    def forward(self,x,t,c):
        h=torch.cat([x,self.time(t),self.cond(c)],1);return self.net(h)
