import torch
import torch.nn as nn
from transformers import AutoModel

class RewardModel(nn.Module):
    def __init__(self, base_model="distilgpt2"):
        # Default swapped from the gated meta-llama/Meta-Llama-3-8B to an
        # open, ungated model so this runs without HF access approval /
        # an auth token. Pass a bigger base_model if you have access.
        super().__init__()
        self.backbone = AutoModel.from_pretrained(base_model)
        hidden = self.backbone.config.hidden_size
        self.reward_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(),
            nn.Linear(hidden // 2, 1)
        )

    def forward(self, input_ids, attention_mask):
        out = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        # Pool the last *non-padded* token per sequence rather than
        # always index -1, which would grab a PAD token for shorter
        # sequences in a padded batch.
        seq_lens = attention_mask.sum(dim=1) - 1
        last_hidden = out.last_hidden_state[torch.arange(out.last_hidden_state.size(0)), seq_lens]
        reward = self.reward_head(last_hidden)
        return reward.squeeze(-1)  # [B]
