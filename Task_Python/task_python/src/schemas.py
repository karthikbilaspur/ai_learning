
from pydantic import BaseModel, Field
from typing import Any, Optional, List

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
    email: str
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ToolRequest(BaseModel):
    tool: str
    params: dict = {}

class ToolResponse(BaseModel):
    tool: str
    status: str
    result: Any
    logs: Optional[str] = None
