from torch.utils.data import Dataset
import json

class PreferenceDataset(Dataset):
    def __init__(self, jsonl_path):
        self.data=[]
        with open(jsonl_path) as f:
            for line in f:
                ex=json.loads(line)
                # ex: {"prompt": str, "chosen": str, "rejected": str}
                self.data.append(ex)
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]

def collate_fn(batch, tokenizer):
    prompts = [b["prompt"] for b in batch]
    chosen = [b["prompt"]+b["chosen"] for b in batch]
    rejected = [b["prompt"]+b["rejected"] for b in batch]
    tok_c = tokenizer(chosen, padding=True, truncation=True, return_tensors="pt")
    tok_r = tokenizer(rejected, padding=True, truncation=True, return_tensors="pt")
    return tok_c, tok_r
