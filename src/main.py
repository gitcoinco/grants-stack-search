import uvicorn
import logging
import socket
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.config import Settings
from src.util import get_json_log_formatter, parse_applicaton_file_locators
from src.data import Data


load_dotenv()
settings = Settings()  # type: ignore -- TODO investigate why this is necessary

logger = logging.getLogger()
logger.setLevel(settings.log_level)
logHandler = logging.StreamHandler()
logHandler.setFormatter(
    get_json_log_formatter(
        hostname=socket.gethostname(),
        deployment_environment=settings.deployment_environment,
    ),
)
logger.addHandler(logHandler)


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
        func=update_dataset,
        trigger="cron",
        minute="0,30",
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
