import logging
from typing import Any, Dict
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.config import Settings
from src.data import InputDocument, load_input_documents_from_applications_dir
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

input_documents = load_input_documents_from_applications_dir(
    settings.applications_dir, chain_id=settings.chain_id
)

# TODO create a Dataset class
input_documents_index: Dict[str, InputDocument] = {}
for input_document in input_documents:
    input_documents_index[
        input_document.document.metadata["application_ref"]
    ] = input_document


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
# UTILITIES


def get_application_by_ref(application_ref: str) -> SearchResult | None:
    input_document = input_documents_index.get(application_ref)
    if input_document is None:
        return None
    else:
        # TODO return an Application object without search metadata
        return SearchResult.from_content_and_metadata(
            content=input_document.document.page_content,
            metadata=input_document.document.metadata,
            search_score=0,
            search_type="fulltext",
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
            "results_names_with_search_meta": [
                {"name": r.name, "meta": r.search_meta} for r in results
            ],
        },
    )


@app.get("/applications/{application_ref}")
def get_application(application_ref: str) -> SearchResult | None:
    return get_application_by_ref(application_ref)


app.mount("/static", StaticFiles(directory="static"), name="static")
