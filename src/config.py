from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    application_files_locators: str
    max_search_results: int = 100
    storage_dir: str
    http_workers: int | None = None
    port: int = 8000
    bind_address: str = "0.0.0.0"
    auto_reload: bool = False
    indexer_base_url: str = "https://indexer-production.fly.dev"
    cache_max_age_seconds: int = 60 * 10
    log_level: (
        Literal["TRACE"]
        | Literal["DEBUG"]
        | Literal["INFO"]
        | Literal["WARNING"]
        | Literal["ERROR"]
    )
