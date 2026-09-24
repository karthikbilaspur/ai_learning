"""FedProx local optimizer: FedAvg plus a proximal penalty to the global model."""
import torch

def train_fedprox(model, loader, global_state, epochs=1, lr=0.01, mu=0.01, device='cpu'):
    model.to(device); model.train(); opt=torch.optim.SGD(model.parameters(),lr=lr)
    refs={k:v.detach().to(device) for k,v in global_state.items()}
    for _ in range(epochs):
        for x,y in loader:
            x,y=x.to(device),y.to(device); logits=model(x)
            loss=torch.nn.functional.cross_entropy(logits,y)
            prox=sum((p-refs[n]).pow(2).sum() for n,p in model.named_parameters())
            loss=loss + 0.5*mu*prox
            opt.zero_grad(); loss.backward(); opt.step()
    return model
