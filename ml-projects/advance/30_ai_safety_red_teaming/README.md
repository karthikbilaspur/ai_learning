# 30 Ai Safety Red Teaming -- Level 1

Automated red teaming & jailbreak detection.

## What's here
- `data/goals.txt` - a small set of sample attack goals (none was included)
- `src/target_model.py` - **new**: concrete attack targets (a
  dependency-free refusal stub, a local HF model, or OpenAI) --
  previously `target_model_fn` had no implementation to pass in
- `src/red_team.py` - target is now fully configurable (no longer forces
  an OpenAI dependency); `pair_attack` falls back to using the target as
  its own attacker if no separate attacker model is given; docstrings
  are honest that `gcg_style` is a black-box random-search stand-in, not real GCG
- `src/guardrail.py` - default swapped from gated `Llama-Guard-3-8B` to
  open `unitary/toxic-bert`; the keyword filter is now labeled
  `KeywordGuardrail` and documented as *not* being the real NeMo
  Guardrails library
- `src/main.py` - **new**: runs attacks, computes Attack Success Rate,
  and (optionally) checks how much a guardrail would have blocked

## Run
```bash
pip install -r ../requirements.txt
python src/main.py --target stub                    # fastest, fully offline
python src/main.py --target hf --guardrail           # real small model + keyword guardrail
```
