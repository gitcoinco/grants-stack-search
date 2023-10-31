import logging
from pprint import pprint
from typing import Any
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.config import Settings
from src.data import load_projects_json, load_applications_dir
from src.search import SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_hybrid import combine_results
from src.search_query import SearchQuery
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

project_docs = load_applications_dir(settings.applications_dir)

semantic_search_engine = SemanticSearchEngine()
if settings.chromadb_persistence_dir is None:
    semantic_search_engine.index_projects(project_docs)
else:
    try:
        semantic_search_engine.load(settings.chromadb_persistence_dir)
    except Exception as e:
        semantic_search_engine.index_projects(
            project_docs, persist_directory=settings.chromadb_persistence_dir
        )

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


class SearchResponse(BaseModel):
    results: list[SearchResult]
    debug: Any


######################################################################
# API ROUTES


@app.get("/search")
def search(q: str) -> SearchResponse:
    try:
        query = SearchQuery(q)
    except Exception as e:
        logging.error("error parsing query: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    if not query.is_valid:
        return SearchResponse(results=[], debug={})

    if query.params.strategy == "semantic":
        results = semantic_search_engine.search(query.string)
    elif query.params.strategy == "fulltext":
        results = fulltext_search_engine.search(query.string)
    elif query.params.strategy == "hybrid":
        results = combine_results(
            semantic_results=semantic_search_engine.search(query.string),
            fulltext_results=fulltext_search_engine.search(query.string),
            fulltext_std_dev_factor=query.params.hybrid_search_fulltext_std_dev_factor,
            semantic_score_cutoff=query.params.hybrid_search_semantic_score_cutoff,
        )
    else:
        raise Exception('Unknown strategy: "%s"' % query.params.strategy)

    return SearchResponse(
        results=results[0:MAX_RESULTS_PER_STRATEGY],
        debug={
            "query_string": query.string,
            "query_params": query.params.model_dump(),
            "result_count": len(results),
            "results_names_with_scores": [
                {"name": r.name, "score": r.score} for r in results
            ],
        },
    )


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> SearchResult | None:
    return get_project_by_id(project_id)


app.mount("/static", StaticFiles(directory="static"), name="static")
