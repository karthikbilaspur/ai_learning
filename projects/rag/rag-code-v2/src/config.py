from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "Production RAG Agent"
    app_version: str = "5.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    data_path: str = "data/docs.json"
    index_dir: str = "data/index"
    force_rebuild_index: bool = False

    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2
    llm_temperature: float = 0.1

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_k: int = Field(5, ge=1, le=50)
    retrieval_candidates: int = Field(20, ge=1, le=200)
    hybrid_alpha: float = Field(0.6, ge=0.0, le=1.0)
    reranker_enabled: bool = True
    chunk_size: int = Field(300, ge=50, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)

    cost_per_1k_prompt: float = 0.00015
    cost_per_1k_completion: float = 0.0006
    monthly_budget_usd: float = 50.0

    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    max_question_length: int = 2000

    @field_validator("llm_provider")
    @classmethod
    def valid_provider(cls, v: str) -> str:
        v=v.lower().strip()
        if v not in {"openai", "mock"}: raise ValueError("llm_provider must be openai or mock")
        return v

    @property
    def index_path(self) -> Path: return Path(self.index_dir)

@lru_cache
def get_settings() -> Settings: return Settings()

settings = get_settings()
