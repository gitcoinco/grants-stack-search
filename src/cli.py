import logging
import rich
from dotenv import load_dotenv
from data import load_project_dataset_into_chroma_db
from config import Settings

######################################################################
# SETUP

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()
settings = Settings()  # type: ignore


######################################################################
# STATE

db = load_project_dataset_into_chroma_db(settings.projects_json_path)


######################################################################
# MAIN LOOP

while True:
    try:
        query = input("> ")
        print()
        docs = db.similarity_search(query)
        for doc in docs:
            rich.print(" - ", doc.metadata["name"])
        print()
    except EOFError:
        break
