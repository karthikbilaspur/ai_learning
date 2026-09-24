"""Direct Preference Optimization (DPO) trainer for the existing preference JSONL format."""
import torch, torch.nn.functional as F

def sequence_logprob(model,input_ids,attention_mask):
    out=model(input_ids=input_ids,attention_mask=attention_mask);logp=F.log_softmax(out.logits,dim=-1)
    shifted_ids=input_ids[:,1:]; shifted_mask=attention_mask[:,1:]; chosen=logp[:,:-1].gather(-1,shifted_ids.unsqueeze(-1)).squeeze(-1)
    return (chosen*shifted_mask).sum(1)/(shifted_mask.sum(1).clamp_min(1))

def dpo_loss(policy_chosen,policy_rejected,ref_chosen,ref_rejected,beta=.1):
    advantage=(policy_chosen-policy_rejected)-(ref_chosen-ref_rejected)
    return -F.logsigmoid(beta*advantage).mean()

@torch.no_grad()
def preference_accuracy(policy_c,policy_r): return float((policy_c>policy_r).float().mean().item())
