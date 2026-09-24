import time, torch, psutil
from transformers import AutoModel, AutoTokenizer

def benchmark(model, tokenizer, prompt="Hello world", n=20, label="model"):
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    model.eval()
    for _ in range(3):
        with torch.no_grad():
            model(**inputs)
    start = time.time()
    for _ in range(n):
        with torch.no_grad():
            model(**inputs)
    latency = (time.time() - start) / n * 1000
    mem = (torch.cuda.max_memory_allocated() / 1e6 if torch.cuda.is_available()
           else psutil.Process().memory_info().rss / 1e6)
    print(f"[{label}] Latency: {latency:.1f} ms | Mem: {mem:.1f} MB")
    return {"label": label, "latency_ms": latency, "mem_mb": mem}
