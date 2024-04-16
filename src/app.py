from contextlib import asynccontextmanager
# from pythonjsonlogger import jsonlogger
import socket
import time
import logging
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from src.data import Data, ApplicationSummary
from src.search import SearchResultMeta
from src.search_hybrid import combine_results
from src.search_query import SearchQuery
from src.config import Settings
from src.util import get_json_log_formatter

######################################################################
# CONFIGURATION

HOSTNAME = socket.gethostname()

settings = Settings()  # type: ignore -- TODO investigate why this is necessary


@asynccontextmanager
async def lifespan(app: FastAPI):
    json_log_formatter = get_json_log_formatter(
        hostname=HOSTNAME, deployment_environment=settings.deployment_environment
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    root_log_handler = logging.StreamHandler()
    root_log_handler.setFormatter(json_log_formatter)
    root_logger.addHandler(root_log_handler)

    class HealthCheckFilter(logging.Filter):
        def filter(self, record):
            return record.getMessage().find("GET /health HTTP") == -1

    access_logger = logging.getLogger("uvicorn.access")
    # Remove existing logger otherwise access messages will be printed twice, once plain, once in json
    access_logger.handlers.clear()
    access_log_handler = logging.StreamHandler()
    access_log_handler.setFormatter(json_log_formatter)
    access_logger.addHandler(access_log_handler)
    access_logger.addFilter(HealthCheckFilter())

    yield


######################################################################
# STATE


data = Data(settings.storage_dir)
data.reload()

app = FastAPI(lifespan=lifespan)

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=data.reload,
    trigger="cron",
    minute="5,35",
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
async def search(q: str, response: Response) -> SearchResponse:
    try:
        query = SearchQuery(
            q,
            default_hybrid_search_fulltext_std_dev_factor=1,
            default_semantic_score_cutoff=0.35,
        )
    except Exception as e:
        logging.error("Error parsing query '%s': %s", q, e)
        raise HTTPException(status_code=400, detail=str(e))

    if query.params.strategy == "semantic":
        results = data.semantic_search_engine.search(
            query.string, min_score=query.params.semantic_score_cutoff
        )

    elif query.params.strategy == "fulltext":
        results = data.fulltext_search_engine.search(query.string)

    elif query.params.strategy == "hybrid":
        semantic_results = data.semantic_search_engine.search(
            query.string, min_score=query.params.semantic_score_cutoff
        )
        fulltext_results = data.fulltext_search_engine.search(query.string)
        results = combine_results(
            semantic_results=semantic_results,
            fulltext_results=fulltext_results,
            fulltext_std_dev_factor=query.params.hybrid_search_fulltext_std_dev_factor,
        )
    else:
        raise Exception('Unknown strategy: "%s"' % query.params.strategy)

    response.headers["Cache-Control"] = f"max-age={settings.cache_max_age_seconds}"

    # Debugging intermittent issue. Other half of this is in data.py /
    # Data / reload.

    search_results: List[SearchResult] = []
    for r in results[0 : settings.max_search_results]:
        try:
            search_results.append(
                SearchResult(
                    meta=SearchResultMeta(search_type=r.type, search_score=r.score),
                    data=data.application_summaries_by_ref[r.ref],
                )
            )
        except Exception as e:
            logging.warn(
                "Anomaly detected: could not retrieve application %s: %s", r.ref, e
            )

    return SearchResponse(results=search_results)

    # return SearchResponse(
    #     results=[
    #         SearchResult(
    #             meta=SearchResultMeta(search_type=r.type, search_score=r.score),
    #             data=data.application_summaries_by_ref[r.ref],
    #         )
    #         for r in results[0 : settings.max_search_results]
    #     ]
    # )


@app.get("/applications")
async def get_applications(response: Response) -> ApplicationsResponse:
    response.headers["Cache-Control"] = f"max-age={settings.cache_max_age_seconds}"
    return ApplicationsResponse(
        application_summaries=list(data.application_summaries_by_ref.values())
    )


@app.get("/health")
async def get_healthcheck():
    return {"ok": True}


app.mount("/static", StaticFiles(directory="static"), name="static")
