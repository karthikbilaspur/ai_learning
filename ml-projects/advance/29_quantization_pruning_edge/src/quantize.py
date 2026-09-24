import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Defaults swapped from the gated meta-llama/Meta-Llama-3-8B to an open,
# ungated model so these run without HF access approval / an auth token.
DEFAULT_MODEL = "distilgpt2"

def quantize_int8(model_id=DEFAULT_MODEL):
    model = AutoModelForCausalLM.from_pretrained(model_id, load_in_8bit=True, device_map="auto")
    print("Loaded INT8 model")
    return model

def quantize_gptq(model_id=DEFAULT_MODEL, calib_data=None, out_dir="model-gptq-4bit"):
    from optimum.gptq import GPTQQuantizer
    calib_data = calib_data or [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning models can be compressed for edge deployment.",
    ]
    quantizer = GPTQQuantizer(bits=4, dataset=calib_data, block_name_to_quantize="transformer.h")
    model = AutoModelForCausalLM.from_pretrained(model_id)
    quantized = quantizer.quantize_model(model, tokenizer=AutoTokenizer.from_pretrained(model_id))
    quantized.save_pretrained(out_dir)
    print(f"Saved 4-bit GPTQ model to {out_dir}")
    return quantized

def export_onnx(model_id="bert-base-uncased", out_path="model.onnx"):
    from optimum.onnxruntime import ORTModelForSequenceClassification
    model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
    model.save_pretrained(out_path)
    print(f"ONNX exported to {out_path}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["int8", "gptq", "onnx"], default="int8")
    p.add_argument("--model_id", default=DEFAULT_MODEL)
    args = p.parse_args()
    if args.mode == "int8":
        quantize_int8(args.model_id)
    elif args.mode == "gptq":
        quantize_gptq(args.model_id)
    else:
        export_onnx(args.model_id if args.model_id != DEFAULT_MODEL else "bert-base-uncased")
