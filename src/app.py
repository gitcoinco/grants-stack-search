import socket
import time
import logging
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.data import Data
from src.search import ApplicationSummary, SearchResultMeta
from src.search_hybrid import combine_results
from src.search_query import SearchQuery
from src.config import Settings

######################################################################
# CONFIGURATION

settings = Settings()  # type: ignore -- TODO investigate why this is necessary
HOSTNAME = socket.gethostname()


######################################################################
# STATE


data = Data(settings.storage_dir)
data.reload()

app = FastAPI()

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: data.reload(),
    "interval",
    seconds=settings.reload_interval_seconds,
    max_instances=1,
    name="Reload application data",
)
scheduler.start()


######################################################################
# MIDDLEWARES


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_hostname_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Hostname"] = HOSTNAME
    return response


######################################################################
# API TYPES


class SearchResult(BaseModel):
    meta: SearchResultMeta
    data: ApplicationSummary


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(serialization_alias="results")


class ApplicationsResponse(BaseModel):
    application_summaries: List[ApplicationSummary] = Field(
        serialization_alias="applicationSummaries"
    )


######################################################################
# API ROUTES


@app.get("/search")
async def search(q: str) -> SearchResponse:
    try:
        query = SearchQuery(q)
    except Exception as e:
        logging.error("error parsing query: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    # TODO rename to is_empty?
    if not query.is_valid:
        return SearchResponse(results=[])

    if query.params.strategy == "semantic":
        results = data.semantic_search_engine.search(query.string)
    elif query.params.strategy == "fulltext":
        results = data.fulltext_search_engine.search(query.string)
    elif query.params.strategy == "hybrid":
        semantic_results = data.semantic_search_engine.search(query.string)
        fulltext_results = data.fulltext_search_engine.search(query.string)
        results = combine_results(
            semantic_results=semantic_results,
            fulltext_results=fulltext_results,
            fulltext_std_dev_factor=query.params.hybrid_search_fulltext_std_dev_factor,
            semantic_score_cutoff=query.params.hybrid_search_semantic_score_cutoff,
        )
    else:
        raise Exception('Unknown strategy: "%s"' % query.params.strategy)

    return SearchResponse(
        results=[
            SearchResult(
                meta=SearchResultMeta(search_type=r.type, search_score=r.score),
                data=data.application_summaries_by_ref[r.ref],
            )
            for r in results[0 : settings.max_results_per_search_strategy]
        ]
    )


@app.get("/applications")
async def get_applications() -> ApplicationsResponse:
    return ApplicationsResponse(
        application_summaries=list(data.application_summaries_by_ref.values())
    )


app.mount("/static", StaticFiles(directory="static"), name="static")
