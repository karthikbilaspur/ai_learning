import evaluate
from datasets import load_dataset

class LLMEvalSuite:
    def __init__(self, model_fn):
        self.model_fn = model_fn  # callable(prompt) -> response
        self._metrics = {}

    def _metric(self, name, **load_kwargs):
        if name not in self._metrics:
            self._metrics[name] = evaluate.load(name, **load_kwargs)
        return self._metrics[name]

    def eval_truthfulqa(self, n=20):
        ds = load_dataset("truthful_qa", "generation")["validation"].select(range(n))
        correct = 0
        for ex in ds:
            prompt = ex["question"]
            pred = self.model_fn(prompt).lower()
            best_answers = [a.lower() for a in ex.get("correct_answers", [])]
            if any(a in pred for a in best_answers if a):
                correct += 1
        return {"truthfulqa_acc": correct / max(n, 1)}

    def eval_hallucination(self, prompts):
        """Heuristic hallucination proxy: flags responses that cite a
        source (arxiv/http link) without being asked to -- a real
        pipeline would fact-check the citation against a retriever
        instead of this naive keyword check."""
        flagged = 0
        for p in prompts:
            resp = self.model_fn(p)
            if "arxiv" in resp.lower() or "http" in resp.lower():
                flagged += 1
        return {"unverified_citation_rate": flagged / max(len(prompts), 1)}

    def eval_toxicity(self, prompts):
        results = [self.model_fn(p) for p in prompts]
        tox = self._metric("toxicity", module_type="measurement").compute(predictions=results)
        return {"toxicity": tox}

    def eval_bias_pairs(self, prompt_pairs):
        """Simple counterfactual-fairness probe: for pairs of prompts that
        differ only in a protected attribute (e.g. names/pronouns), flags
        cases where sentiment/toxicity diverges a lot between the two.
        prompt_pairs: list of (prompt_a, prompt_b) tuples."""
        tox_metric = self._metric("toxicity", module_type="measurement")
        gaps = []
        for a, b in prompt_pairs:
            resp_a, resp_b = self.model_fn(a), self.model_fn(b)
            tox_a = tox_metric.compute(predictions=[resp_a])["toxicity"][0]
            tox_b = tox_metric.compute(predictions=[resp_b])["toxicity"][0]
            gaps.append(abs(tox_a - tox_b))
        avg_gap = sum(gaps) / max(len(gaps), 1)
        return {"bias_toxicity_gap": avg_gap, "n_pairs": len(prompt_pairs)}
