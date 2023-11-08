from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    application_files_locators: str
    max_results_per_search_strategy: int = 25
    storage_dir: str
    http_workers: int | None = None
    port: int = 8000
    bind_address: str = "0.0.0.0"
    auto_reload: bool = False
    indexer_base_url: str = "https://indexer-production.fly.dev"
    update_interval_seconds: int = 60 * 10
    reload_interval_seconds: int = 60 * 1
    log_level: (
        Literal["TRACE"]
        | Literal["DEBUG"]
        | Literal["INFO"]
        | Literal["WARNING"]
        | Literal["ERROR"]
    )
