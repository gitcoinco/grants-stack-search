import logging
from typing import Dict, List
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.config import Settings
from src.data import load_input_documents_from_applications_dir
from src.search import ApplicationSummary, SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_hybrid import combine_results
from src.search_query import SearchQuery
from src.search_semantic import SemanticSearchEngine


######################################################################
# SETUP

MAX_RESULTS_PER_STRATEGY = 25
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
load_dotenv()
settings = Settings()  # type: ignore -- TODO investigate why this is necessary
SearchResult.IPFS_GATEWAY_BASE = settings.ipfs_gateway


######################################################################
# STATE

input_documents = load_input_documents_from_applications_dir(
    settings.applications_dir, chain_id=settings.chain_id
)

application_summaries_by_ref: Dict[str, ApplicationSummary] = {}
for input_document in input_documents:
    application_summaries_by_ref[
        input_document.document.metadata["application_ref"]
    ] = ApplicationSummary.from_metadata(input_document.document.metadata)


semantic_search_engine = SemanticSearchEngine()
if settings.chromadb_persistence_dir is None:
    semantic_search_engine.index(input_documents)
else:
    try:
        semantic_search_engine.load(settings.chromadb_persistence_dir)
    except Exception as e:
        semantic_search_engine.index(
            input_documents, persist_directory=settings.chromadb_persistence_dir
        )

fulltext_search_engine = FullTextSearchEngine()
fulltext_search_engine.index(input_documents)


app = FastAPI()

######################################################################
# API TYPES


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(serialization_alias="results")


class ApplicationsResponse(BaseModel):
    application_summaries: List[ApplicationSummary] = Field(
        serialization_alias="applicationSummaries"
    )


class ApplicationResponse(BaseModel):
    application_summary: ApplicationSummary = Field(
        serialization_alias="applicationSummary"
    )


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
        return SearchResponse(results=[])

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
    )


@app.get("/applications")
def get_applications() -> ApplicationsResponse:
    return ApplicationsResponse(
        application_summaries=list(application_summaries_by_ref.values())
    )


@app.get("/applications/{application_ref}")
def get_application(application_ref: str) -> ApplicationResponse | None:
    application_summary = application_summaries_by_ref.get(application_ref)
    if application_summary is None:
        return None
    else:
        return ApplicationResponse(application_summary=application_summary)


app.mount("/static", StaticFiles(directory="static"), name="static")
