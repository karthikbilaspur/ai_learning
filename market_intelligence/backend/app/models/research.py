from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class ResearchRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str = Field(index=True)
    structured_data: Optional[str] = None  # Stored as JSON string
    final_report: str
    created_at: datetime = Field(default_factory=datetime.utcnow)