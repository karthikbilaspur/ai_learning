import torch.nn.functional as F, torch

def distillation_loss(student_logits, teacher_logits, labels, T=4.0, alpha=0.7):
    # KL divergence + CE
    soft_loss = F.kl_div(
        F.log_softmax(student_logits/T, dim=1),
        F.softmax(teacher_logits/T, dim=1),
        reduction='batchmean'
    ) * (T*T)
    hard_loss = F.cross_entropy(student_logits, labels)
    return alpha*soft_loss + (1-alpha)*hard_loss

def train_distill(student, teacher, loader, epochs=5):
    teacher.eval()
    opt = torch.optim.AdamW(student.parameters(), lr=5e-5)
    for epoch in range(epochs):
        for x,y in loader:
            with torch.no_grad(): t_logits = teacher(x)
            s_logits = student(x)
            loss = distillation_loss(s_logits, t_logits, y)
            opt.zero_grad(); loss.backward(); opt.step()
        print(f"Distill Epoch {epoch} Loss {loss.item():.4f}")
