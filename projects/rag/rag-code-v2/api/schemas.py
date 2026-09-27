from typing import Any,Dict,List,Optional
from pydantic import BaseModel,Field,ConfigDict
class QueryRequest(BaseModel):
 model_config=ConfigDict(extra="forbid")
 question:str=Field(min_length=3,max_length=2000)
 top_k:int=Field(default=5,ge=1,le=20)
 session_id:Optional[str]=Field(default=None,max_length=128)
class Citation(BaseModel): doc_id:str; chunk_id:str; text:str; score:float
class Usage(BaseModel): prompt_tokens:int; completion_tokens:int; total_tokens:int
class QueryResponse(BaseModel): answer:str; citations:List[Citation]; trace_id:str; latency_ms:int; tokens:Usage; cost_usd:float; retrieval_scores:List[float]; tool_calls:List[Dict[str,Any]]
class HealthResponse(BaseModel): status:str; version:str; eval_gate:str
