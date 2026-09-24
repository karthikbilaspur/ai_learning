import torch, torch.nn as nn, torch.nn.functional as F

class NTXentLoss(nn.Module):
    def __init__(self, temperature=0.5):
        super().__init__()
        self.t = temperature
    def forward(self, z_i, z_j):
        # z_i, z_j: [B, D]
        B = z_i.shape[0]
        z = torch.cat([z_i, z_j], dim=0)  # [2B, D]
        sim = F.cosine_similarity(z.unsqueeze(1), z.unsqueeze(0), dim=2)  # [2B, 2B]
        sim = sim / self.t
        # mask self
        mask = torch.eye(2*B, device=z.device).bool()
        sim.masked_fill_(mask, -9e15)
        # positives: i <-> i+B
        positives = torch.cat([torch.diag(sim, B), torch.diag(sim, -B)], dim=0)
        # log-softmax denominator
        exp_sim = torch.exp(sim)
        log_prob = positives - torch.log(exp_sim.sum(dim=1))
        return -log_prob.mean()

def dino_loss(student_out, teacher_out, center, teacher_temp=0.04, student_temp=0.1):
    teacher_out = F.softmax((teacher_out - center) / teacher_temp, dim=-1)
    student_out = F.log_softmax(student_out / student_temp, dim=-1)
    return -(teacher_out * student_out).sum(dim=-1).mean()
