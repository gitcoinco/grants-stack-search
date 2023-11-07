import multiprocessing
import uvicorn
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.config import Settings
from src.util import parse_applicaton_file_locators
from src.data import Data


logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
load_dotenv()
settings = Settings()  # type: ignore -- TODO investigate why this is necessary


def main():
    logging.info("Starting with config: %s", settings)

    Data.ingest_and_persist(
        application_files_locators=parse_applicaton_file_locators(
            settings.application_files_locators
        ),
        storage_dir=settings.storage_dir,
    )

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(update_dataset, "interval", seconds=60 * 10, max_instances=1)
    # scheduler.start()

    if settings.auto_reload is True and settings.http_workers is not None:
        raise Exception("Auto reload and multiple HTTP workers are mutually exclusive.")

    logging.info("Starting HTTP workers...")

    uvicorn.run(
        "app:app",
        host=settings.bind_address,
        reload=settings.auto_reload,
        port=settings.port,
        workers=settings.http_workers,
    )


if __name__ == "__main__":
    main()
