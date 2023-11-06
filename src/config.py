from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    applications_dir: str
    chain_id: int
    chromadb_persistence_dir: Optional[str] = None
    max_results_per_search_strategy: int = 25
