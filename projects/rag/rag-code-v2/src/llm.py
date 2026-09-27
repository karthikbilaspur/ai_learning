from typing import Dict
import re
from .config import settings
from .cost import tracker
from .prompts import SYSTEM_PROMPT,RAG_TEMPLATE

class LLMWrapper:
 def __init__(self): self.provider=settings.llm_provider
 def generate(self,context:str,question:str,tool_history:str="")->Dict:
  prompt=RAG_TEMPLATE.format(context=context,question=question,tool_history=tool_history)
  if self.provider=="openai" and settings.openai_api_key:
   try:
    from openai import OpenAI
    client=OpenAI(api_key=settings.openai_api_key,timeout=settings.llm_timeout_seconds,max_retries=settings.llm_max_retries)
    r=client.chat.completions.create(model=settings.openai_model,messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],temperature=settings.llm_temperature)
    answer=(r.choices[0].message.content or "").strip(); u=r.usage
    usage={"prompt_tokens":u.prompt_tokens,"completion_tokens":u.completion_tokens,"total_tokens":u.total_tokens}; return {"answer":answer,"usage":usage,"cost":tracker.calculate(usage["prompt_tokens"],usage["completion_tokens"])}
   except Exception:
    pass
  # Deterministic offline fallback: return context sentences rather than fabricate facts.
  parts=[x.strip() for x in re.split(r"(?<=[.!?])\s+",context) if x.strip()]
  answer=" ".join(parts[:3]) if parts else "I don't have enough information in the knowledge base to answer that."
  usage={"prompt_tokens":len(prompt)//4,"completion_tokens":len(answer)//4,"total_tokens":len(prompt)//4+len(answer)//4}
  return {"answer":answer,"usage":usage,"cost":tracker.calculate(usage["prompt_tokens"],usage["completion_tokens"])}
