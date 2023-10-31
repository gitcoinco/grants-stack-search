from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ipfs_gateway: str
    applications_dir: str
    chromadb_persistence_dir: Optional[str] = None
