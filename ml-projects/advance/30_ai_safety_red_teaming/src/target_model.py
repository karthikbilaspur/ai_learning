"""Target-model implementations for the red-team harness. Previously
red_team.py hardcoded a `target_model_fn` parameter with no concrete
implementation to pass in, and guardrail.py defaulted to the gated
meta-llama/Llama-Guard-3-8B.
"""
import os

def refusal_stub_target():
    """A toy 'aligned' target that refuses anything matching an obvious
    blocklist and otherwise echoes -- lets you smoke-test the red-team
    harness with zero downloads/API keys."""
    blocked = ["virus", "phishing", "bypass", "hack", "bomb"]
    def _fn(prompt: str) -> str:
        low = prompt.lower()
        if any(b in low for b in blocked):
            return "I'm sorry, I can't help with that."
        return f"Sure, here's some general information about: {prompt[:60]}"
    return _fn

def hf_local_target(model_id="distilgpt2", max_new_tokens=48):
    """A real (if small/uninstructed) local HF model as the attack
    target -- useful for testing prompt-injection templates against an
    actual model rather than a stub."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    model.eval()

    def _fn(prompt: str) -> str:
        inputs = tok(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=max_new_tokens,
                                  do_sample=False, pad_token_id=tok.pad_token_id)
        text = tok.decode(out[0], skip_special_tokens=True)
        return text[len(prompt):].strip() or text.strip()
    return _fn

def openai_target(model="gpt-4o-mini"):
    from openai import OpenAI
    client = OpenAI()
    def _fn(prompt: str) -> str:
        resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    return _fn

def get_target(kind="stub", **kwargs):
    if kind == "stub":
        return refusal_stub_target()
    if kind == "hf":
        return hf_local_target(**kwargs)
    if kind == "openai":
        return openai_target(**kwargs)
    raise ValueError(f"Unknown target kind: {kind}")
