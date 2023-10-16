import logging
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from dotenv import load_dotenv
from src.config import Settings
from src.data import (
    Project,
    load_projects_json,
)
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


######################################################################
# SETUP

MAX_RESULTS_PER_STRATEGY = 8
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()
# how to make `type: ignore` unnecessary here?
settings = Settings()  # type: ignore


######################################################################
# STATE

project_docs = load_projects_json(settings.projects_json_path)

semantic_search_engine = SemanticSearchEngine()
semantic_search_engine.index_projects(project_docs)

fulltext_search_engine = FullTextSearchEngine()
fulltext_search_engine.index_projects(project_docs)

__hack_db = semantic_search_engine.get_db()

app = FastAPI()

######################################################################
# UTILITIES


class ProjectsSearchResponse(BaseModel):
    results: list[Project]


######################################################################
# API ROUTES


@app.get("/semantic-search")
def semantic_search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    # TODO figure out why only four results are returned
    raw_results = semantic_search_engine.search(q)

    projects = [
        Project.from_input_project_document(settings, doc)
        for doc in raw_results[0:MAX_RESULTS_PER_STRATEGY]
    ]

    return ProjectsSearchResponse(results=projects)


@app.get("/fulltext-search")
def fulltext_search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    raw_results = fulltext_search_engine.search(q)

    projects = [
        Project.from_input_project_document(settings, doc)
        for doc in raw_results[0:MAX_RESULTS_PER_STRATEGY]
    ]

    return ProjectsSearchResponse(results=projects)


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> Project | None:
    result = __hack_db.get(project_id)
    if len(result["ids"]) == 0:
        return None
    else:
        return Project.from_content_and_metadata(
            content=result["documents"][0],
            metadata=result["metadatas"][0],
            settings=settings,
        )


app.mount("/static", StaticFiles(directory="static"), name="static")
