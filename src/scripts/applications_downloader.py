from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import requests
from urllib.parse import urljoin


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="applications_downloader_")
    indexer_base_url: str = "https://indexer-production.fly.dev/"
    chain_id: int
    round_ids: str
    download_dir: str


if __name__ == "__main__":
    settings = Settings()  # type: ignore

    round_ids = settings.round_ids.split(",")
    if len(round_ids) == 0:
        raise Exception("No round ids provided")

    os.makedirs(settings.download_dir, exist_ok=True)

    for round_id in round_ids:
        print(f"Downloading applications for round {round_id}...")
        url = urljoin(
            settings.indexer_base_url,
            f"/data/{settings.chain_id}/rounds/{round_id}/applications.json",
        )
        response = requests.get(url)
        response.raise_for_status()
        filepath = os.path.join(settings.download_dir, f"{round_id}.json")
        with open(filepath, "wb") as f:
            f.write(response.content)
