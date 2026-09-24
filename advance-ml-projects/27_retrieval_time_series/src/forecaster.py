import torch, torch.nn as nn

class RAFTForecaster(nn.Module):
    def __init__(self, input_len=96, pred_len=24, hidden=128, k_retrieved=5):
        super().__init__()
        self.k=k_retrieved
        self.encoder = nn.LSTM(input_len, hidden, batch_first=True)
        self.retrieval_encoder = nn.LSTM(input_len, hidden, batch_first=True)
        self.decoder = nn.Sequential(
            nn.Linear(hidden*2, hidden),
            nn.ReLU(),
            nn.Linear(hidden, pred_len)
        )
    def forward(self, x, retrieved):  # x: [B, L], retrieved: [B, K, L]
        _, (h,_)=self.encoder(x.unsqueeze(1))  # [1,B,H]
        h = h.squeeze(0)
        # encode retrieved
        B,K,L = retrieved.shape
        ret = retrieved.view(B*K, L)
        _, (hr,_)=self.retrieval_encoder(ret.unsqueeze(1))
        hr = hr.view(B,K,-1).mean(dim=1)  # avg over K
        fused = torch.cat([h, hr], dim=1)
        return self.decoder(fused)
