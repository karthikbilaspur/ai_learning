import torch.nn.functional as F
from torch_geometric.nn import GATConv, SAGEConv, global_mean_pool
import torch.nn as nn

class FraudGAT(nn.Module):
    def __init__(self, in_dim=3, hidden=64, heads=4):
        super().__init__()
        self.gat1 = GATConv(in_dim, hidden, heads=heads, dropout=0.2)
        self.gat2 = GATConv(hidden*heads, hidden, heads=1, concat=False)
        self.classifier = nn.Sequential(
            nn.Linear(hidden, hidden//2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden//2, 2)
        )
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.elu(self.gat1(x, edge_index))
        x = F.elu(self.gat2(x, edge_index))
        return self.classifier(x)

class FraudGraphSAGE(nn.Module):
    def __init__(self, in_dim=3, hidden=64):
        super().__init__()
        self.sage1 = SAGEConv(in_dim, hidden)
        self.sage2 = SAGEConv(hidden, hidden)
        self.lin = nn.Linear(hidden, 2)
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.sage1(x, edge_index))
        x = F.relu(self.sage2(x, edge_index))
        return self.lin(x)
