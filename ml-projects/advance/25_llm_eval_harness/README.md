# 25 Llm Eval Harness -- Level 1

Automated LLM evaluation: hallucination proxy, toxicity, bias, and an
LLM-as-judge scorer.

## What's here
- `src/model_fn.py` - concrete `model_fn(prompt) -> str` implementations
  (local HF model / OpenAI / an offline echo stub) -- previously nothing
  showed how to actually plug a model in
- `src/evals.py` - hallucination heuristic, toxicity, TruthfulQA
  accuracy, and a new counterfactual bias-pair probe
- `src/judge.py` - GPT-4o-mini-as-judge (raises a clear error if
  `OPENAI_API_KEY` isn't set, instead of failing deep in a batch run)
- `src/report.py` - HTML report (now handles the no-judge-scores case)
- `src/main.py` - runs the full harness end-to-end

## Run
```bash
pip install -r ../requirements.txt
python src/main.py --model echo --n 5                     # fully offline
python src/main.py --model hf --model_id distilgpt2 --n 10
python src/main.py --model openai --judge --n 10           # needs OPENAI_API_KEY
```
