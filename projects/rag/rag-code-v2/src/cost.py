from threading import Lock
from .config import settings

class CostTracker:
    def __init__(self): self._lock=Lock(); self.total_cost=0.0; self.query_costs=[]
    def calculate(self, prompt_tokens:int, completion_tokens:int)->float:
        cost=(prompt_tokens/1000)*settings.cost_per_1k_prompt+(completion_tokens/1000)*settings.cost_per_1k_completion
        with self._lock:
            self.total_cost += cost; self.query_costs.append(cost); self.query_costs=self.query_costs[-1000:]
        return cost
    def cost_per_1k_queries(self)->float:
        with self._lock: return (sum(self.query_costs)/len(self.query_costs)*1000) if self.query_costs else 0.0
    def budget_status(self):
        with self._lock: spent=self.total_cost
        return {"total_spent":spent,"budget":settings.monthly_budget_usd,"remaining":settings.monthly_budget_usd-spent,"over_budget":spent>settings.monthly_budget_usd}
tracker=CostTracker()
