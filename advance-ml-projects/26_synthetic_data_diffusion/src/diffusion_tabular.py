import torch, torch.nn as nn
import math

class TimeEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    def forward(self, t):
        half = self.dim // 2
        emb = math.log(10000) / (half - 1)
        emb = torch.exp(torch.arange(half, device=t.device) * -emb)
        emb = t[:, None] * emb[None, :]
        return torch.cat([torch.sin(emb), torch.cos(emb)], dim=-1)

class TabDDPM(nn.Module):
    def __init__(self, input_dim=10, hidden=256, time_dim=64):
        super().__init__()
        self.time_emb = TimeEmbedding(time_dim)
        self.net = nn.Sequential(
            nn.Linear(input_dim + time_dim, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, input_dim)
        )
    def forward(self, x, t):
        # t: [B] float in [0, 1) or integer step -- caller controls scale
        t_emb = self.time_emb(t)
        h = torch.cat([x, t_emb], dim=1)
        return self.net(h)


class DiffusionSchedule:
    """Holds a single, consistent noise schedule shared by training
    (q_sample) and sampling (p_sample_loop) -- previously these two used
    two different, incompatible schedules."""
    def __init__(self, steps=1000, beta_start=1e-4, beta_end=0.02, device="cpu"):
        self.steps = steps
        self.betas = torch.linspace(beta_start, beta_end, steps, device=device)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)

    def to(self, device):
        self.betas = self.betas.to(device)
        self.alphas = self.alphas.to(device)
        self.alphas_cumprod = self.alphas_cumprod.to(device)
        return self


def q_sample(x0, t, noise, schedule: DiffusionSchedule):
    """Forward diffusion: sample x_t given x0, timestep t (long tensor of
    indices into schedule.alphas_cumprod) and noise."""
    ac = schedule.alphas_cumprod[t]
    sqrt_ac = ac.sqrt().unsqueeze(1)
    sqrt_om = (1 - ac).sqrt().unsqueeze(1)
    return sqrt_ac * x0 + sqrt_om * noise


@torch.no_grad()
def p_sample_loop(model, shape, schedule: DiffusionSchedule, device="cpu"):
    """Reverse diffusion (DDPM ancestral sampling) using the *same*
    schedule the model was trained with."""
    model.eval()
    x = torch.randn(shape, device=device)
    betas = schedule.betas.to(device)
    alphas = schedule.alphas.to(device)
    alphas_cumprod = schedule.alphas_cumprod.to(device)

    for i in reversed(range(schedule.steps)):
        t = torch.full((shape[0],), i, device=device, dtype=torch.long)
        t_norm = t.float() / schedule.steps
        eps = model(x, t_norm)

        alpha_t = alphas[i]
        alpha_cumprod_t = alphas_cumprod[i]
        beta_t = betas[i]

        mean = (1 / alpha_t.sqrt()) * (x - (beta_t / (1 - alpha_cumprod_t).sqrt()) * eps)
        if i > 0:
            noise = torch.randn_like(x)
            x = mean + beta_t.sqrt() * noise
        else:
            x = mean
    return x
