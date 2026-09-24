from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class SafetyGuardrail:
    """Wraps an open, ungated text-classification model as an
    input/output safety filter. Default swapped from the gated
    meta-llama/Llama-Guard-3-8B to `unitary/toxic-bert`, which is public
    and needs no access approval -- swap in Llama-Guard yourself if you
    have access, the interface is unchanged."""

    def __init__(self, model_id="unitary/toxic-bert", unsafe_label_index=1):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
        self.model.eval()
        self.unsafe_label_index = unsafe_label_index

    def is_safe(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.sigmoid(logits) if logits.shape[-1] > 1 else torch.softmax(logits, dim=-1)
        score = probs[0, self.unsafe_label_index].item() if probs.shape[-1] > self.unsafe_label_index else probs[0, -1].item()
        return {"safe": score < 0.5, "unsafe_score": score}

    def filter(self, text):
        res = self.is_safe(text)
        return text if res["safe"] else "[BLOCKED BY GUARDRAIL]"


class KeywordGuardrail:
    """Simple, transparent keyword blocklist -- a fast first line of
    defense to layer in front of SafetyGuardrail, not a replacement for
    the real NeMo Guardrails library (which does rail-based dialogue
    control, not just string matching)."""

    def __init__(self, blocked_phrases=None):
        self.blocked = blocked_phrases or ["how to make a bomb", "how to hack", "child sexual"]

    def check(self, text):
        low = text.lower()
        return not any(b in low for b in self.blocked)
