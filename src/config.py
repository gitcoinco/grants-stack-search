from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ipfs_gateway: str
    projects_json_path: str
    chromadb_persistence_dir: Optional[str] = None
