from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    application_files_locators: str
    max_results_per_search_strategy: int = 25
    storage_dir: str
    http_workers: int | None
    port: int = 8000
    bind_address: str = "0.0.0.0"
    auto_reload: bool = False
