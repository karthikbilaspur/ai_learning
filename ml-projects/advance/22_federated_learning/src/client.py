import flwr as fl
import torch
from model import Net

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, trainloader, valloader):
        self.trainloader = trainloader
        self.valloader = valloader
        self.model = Net()

    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        train(self.model, self.trainloader, epochs=config.get("local_epochs", 1),
              lr=config.get("lr", 0.01))
        return self.get_parameters(config), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, acc = test(self.model, self.valloader)
        return loss, len(self.valloader.dataset), {"accuracy": acc}


def train(net, loader, epochs=1, lr=0.01):
    opt = torch.optim.SGD(net.parameters(), lr=lr)
    net.train()
    for _ in range(epochs):
        for x, y in loader:
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(net(x), y)
            loss.backward(); opt.step()


def test(net, loader):
    net.eval(); loss = 0.0; correct = 0; total = 0
    with torch.no_grad():
        for x, y in loader:
            out = net(x)
            loss += torch.nn.functional.cross_entropy(out, y, reduction="sum").item()
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return loss / max(total, 1), correct / max(total, 1)
