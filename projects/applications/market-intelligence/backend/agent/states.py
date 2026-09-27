from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

# Structured Output Schemas
class PricingTier(BaseModel):
    name: str = Field(description="Name of the plan e.g., Free, Pro, Enterprise")
    price: str = Field(description="Price per month or year")
    key_features: List[str] = Field(description="Top features included in this tier")

class CompetitorProfile(BaseModel):
    company_name: str
    target_audience: str
    pricing_tiers: List[PricingTier]
    key_differentiators: List[str]

# Shared LangGraph Execution State
class MarketResearchState(TypedDict):
    company_name: str
    search_queries: List[str]
    scraped_documents: List[str]
    structured_data: Optional[dict]
    critique_feedback: Optional[str]
    final_report: Optional[str]
    search_retry_count: int