import uvicorn
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.config import Settings
from src.util import parse_applicaton_file_locators
from src.data import Data


load_dotenv()
settings = Settings()  # type: ignore -- TODO investigate why this is necessary
logging.basicConfig(level=settings.log_level, format="%(levelname)s: %(message)s")


def update_dataset():
    Data.ingest_from_application_locators_and_persist(
        application_files_locators=parse_applicaton_file_locators(
            settings.application_files_locators
        ),
        storage_dir=settings.storage_dir,
        indexer_base_url=settings.indexer_base_url,
        first_run=False,
    )


def main():
    logging.info("Starting with config: %s", settings)

    Data.ingest_from_application_locators_and_persist(
        application_files_locators=parse_applicaton_file_locators(
            settings.application_files_locators
        ),
        storage_dir=settings.storage_dir,
        indexer_base_url=settings.indexer_base_url,
        first_run=True,
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_dataset,
        "interval",
        seconds=settings.update_interval_seconds,
        max_instances=1,
        name="Update applications data",
    )
    scheduler.start()

    if settings.auto_reload is True and settings.http_workers is not None:
        raise Exception("Auto reload and multiple HTTP workers are mutually exclusive.")

    logging.info("Starting HTTP workers...")

    uvicorn.run(
        "app:app",
        host=settings.bind_address,
        reload=settings.auto_reload,
        port=settings.port,
        workers=settings.http_workers,
        reload_includes=["src"],
    )


if __name__ == "__main__":
    main()
