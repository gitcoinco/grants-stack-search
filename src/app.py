import logging
from typing import Union, Literal
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from dotenv import load_dotenv
from src.config import Settings
from src.data import load_projects_json
from src.search import SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_hybrid import combine_results
from src.search_semantic import SemanticSearchEngine


######################################################################
# SETUP

MAX_RESULTS_PER_STRATEGY = 8
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
load_dotenv()
# how to make `type: ignore` unnecessary here?
settings = Settings()  # type: ignore
SearchResult.IPFS_GATEWAY_BASE = settings.ipfs_gateway


######################################################################
# STATE

project_docs = load_projects_json(settings.projects_json_path)

semantic_search_engine = SemanticSearchEngine()
try:
    semantic_search_engine.load(settings.chromadb_persistence_dir)
except Exception as e:
    semantic_search_engine.index_projects(project_docs)

fulltext_search_engine = FullTextSearchEngine()
fulltext_search_engine.index_projects(project_docs)


app = FastAPI()

######################################################################
# UTILITIES


def get_project_by_id(project_id: str) -> SearchResult | None:
    db = semantic_search_engine._hack_get_db()
    result = db.get(project_id)
    if len(result["ids"]) == 0:
        return None
    else:
        return SearchResult.from_content_and_metadata(
            content=result["documents"][0], metadata=result["metadatas"][0], score=1
        )


class ProjectsSearchResponse(BaseModel):
    results: list[SearchResult]


######################################################################
# API ROUTES


@app.get("/semantic-search")
def semantic_search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    results = semantic_search_engine.search(q)

    logging.debug(
        "semantic search for '%s' returned %d results: %s",
        q,
        len(results),
        [{"name": r.name, "score": r.score} for r in results],
    )

    return ProjectsSearchResponse(results=results[0:MAX_RESULTS_PER_STRATEGY])


@app.get("/fulltext-search")
def fulltext_search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    results = fulltext_search_engine.search(q)

    logging.debug(
        "fulltext search for '%s' returned %d results: %s",
        q,
        len(results),
        [{"name": r.name, "score": r.score} for r in results],
    )

    return ProjectsSearchResponse(results=results[0:MAX_RESULTS_PER_STRATEGY])


@app.get("/hybrid-search")
def hybrid_search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    results = combine_results(
        semantic_results=semantic_search_engine.search(q),
        fulltext_results=fulltext_search_engine.search(q),
    )

    logging.debug(
        "hybrid search for '%s' returned %d results: %s",
        q,
        len(results),
        [{"name": r.name, "score": r.score} for r in results],
    )

    return ProjectsSearchResponse(results=results[0:MAX_RESULTS_PER_STRATEGY])


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> SearchResult | None:
    return get_project_by_id(project_id)


app.mount("/static", StaticFiles(directory="static"), name="static")
