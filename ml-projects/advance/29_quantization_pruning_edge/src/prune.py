import torch, torch.nn.utils.prune as prune

def magnitude_prune(model, amount=0.3):
    """Unstructured L1 magnitude pruning on every Linear layer."""
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            prune.l1_unstructured(module, name='weight', amount=amount)
            prune.remove(module, 'weight')
    return model

def structured_prune_heads(model, heads_per_layer_to_prune=2):
    """Structured attention-head pruning for Hugging Face transformer
    models that expose `.prune_heads()` (BERT/GPT-2/RoBERTa-style
    encoders/decoders via the `PreTrainedModel` API). Picks the heads
    with the smallest L2 norm of their output-projection weights as the
    least-important ones to drop, per layer.

    Previously this function had an empty body (`pass`) and pruned
    nothing.
    """
    if not hasattr(model, "prune_heads"):
        raise TypeError(
            "structured_prune_heads expects a Hugging Face PreTrainedModel "
            "that implements prune_heads() (e.g. BERT/GPT-2 style models)."
        )

    config = model.config
    num_layers = getattr(config, "n_layer", None) or getattr(config, "num_hidden_layers", None)
    num_heads = getattr(config, "n_head", None) or getattr(config, "num_attention_heads", None)
    if num_layers is None or num_heads is None:
        raise ValueError("Could not infer num_layers/num_heads from model.config")

    heads_to_prune = {}
    for layer_idx in range(num_layers):
        # Rank heads by the norm of their attention output weights and
        # drop the smallest `heads_per_layer_to_prune`.
        attn = _find_attention_module(model, layer_idx)
        if attn is None:
            continue
        head_norms = _per_head_norms(attn, num_heads)
        weakest = sorted(range(num_heads), key=lambda h: head_norms[h])[:heads_per_layer_to_prune]
        heads_to_prune[layer_idx] = weakest

    model.prune_heads(heads_to_prune)
    return model

def _find_attention_module(model, layer_idx):
    # Works for GPT-2 (transformer.h[i].attn) and BERT (encoder.layer[i].attention).
    try:
        return model.transformer.h[layer_idx].attn
    except AttributeError:
        pass
    try:
        return model.encoder.layer[layer_idx].attention
    except AttributeError:
        return None

def _per_head_norms(attn_module, num_heads):
    # Find the output-projection weight matrix and compute a per-head L2 norm slice.
    out_proj = getattr(attn_module, "c_proj", None) or getattr(attn_module, "output", None)
    if out_proj is None:
        return [1.0] * num_heads  # fall back to "prune arbitrary heads" if shape is unknown
    weight = out_proj.weight if hasattr(out_proj, "weight") else out_proj.dense.weight
    head_dim = weight.shape[0] // num_heads
    norms = []
    for h in range(num_heads):
        chunk = weight[h * head_dim:(h + 1) * head_dim]
        norms.append(chunk.norm().item())
    return norms

def check_sparsity(model):
    total = 0; zeros = 0
    for p in model.parameters():
        total += p.numel(); zeros += (p == 0).sum().item()
    sparsity = zeros / total * 100 if total else 0.0
    print(f"Sparsity {sparsity:.2f}%")
    return sparsity
