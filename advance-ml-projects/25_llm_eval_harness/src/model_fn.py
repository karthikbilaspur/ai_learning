"""Concrete `model_fn(prompt) -> str` implementations to plug into
LLMEvalSuite / LLMAsJudge. Previously nothing in this project showed how
to actually call a model under test.
"""
import os

def hf_local_model_fn(model_id="distilgpt2", max_new_tokens=64, device=None):
    """Wraps a small local Hugging Face causal LM as a model_fn. Good
    default for running the harness with no API key."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    model.eval()

    def _fn(prompt: str) -> str:
        inputs = tok(prompt, return_tensors="pt").to(device)
        import torch as _torch
        with _torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=max_new_tokens,
                                  do_sample=False, pad_token_id=tok.pad_token_id)
        text = tok.decode(out[0], skip_special_tokens=True)
        return text[len(prompt):].strip() or text.strip()
    return _fn

def openai_model_fn(model="gpt-4o-mini"):
    """Wraps the OpenAI chat API as a model_fn. Requires OPENAI_API_KEY."""
    from openai import OpenAI
    client = OpenAI()

    def _fn(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    return _fn

def echo_model_fn():
    """Trivial offline stand-in for smoke-testing the harness with no
    model download / no API key at all."""
    def _fn(prompt: str) -> str:
        return f"I don't know. ({prompt[:40]})"
    return _fn

def get_model_fn(kind="hf", **kwargs):
    if kind == "hf":
        return hf_local_model_fn(**kwargs)
    if kind == "openai":
        return openai_model_fn(**kwargs)
    if kind == "echo":
        return echo_model_fn()
    raise ValueError(f"Unknown model_fn kind: {kind}")
