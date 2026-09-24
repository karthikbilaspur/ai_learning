import torch.nn as nn, torch.nn.functional as F
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3,32,3,1)
        self.conv2 = nn.Conv2d(32,64,3,1)
        self.fc1 = nn.Linear(64*6*6,128)
        self.fc2 = nn.Linear(128,10)
    def forward(self, x):
        x = F.relu(self.conv1(x)); x = F.max_pool2d(x,2)
        x = F.relu(self.conv2(x)); x = F.max_pool2d(x,2)
        x = x.view(-1,64*6*6); x = F.relu(self.fc1(x))
        return self.fc2(x)
