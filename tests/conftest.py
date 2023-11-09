from dataclasses import dataclass
import os
from typing import List, Dict
from src.data import InputDocument, deprecated_load_input_documents_from_projects_json
import pytest
import logging
from src.search import ApplicationSummary, SearchEngineResult
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


logging.basicConfig(level=logging.INFO)


@dataclass
class SearchResultsFixture:
    fulltext_black_hare: List[SearchEngineResult]
    semantic_black_hare: List[SearchEngineResult]
    fulltext_education: List[SearchEngineResult]
    semantic_education: List[SearchEngineResult]
    fulltext_nature_preservation: List[SearchEngineResult]
    semantic_nature_preservation: List[SearchEngineResult]
    fulltext_blck_hare: List[SearchEngineResult]
    semantic_blck_hare: List[SearchEngineResult]


@dataclass
class SearchEnginesFixture:
    semantic: SemanticSearchEngine
    fulltext: FullTextSearchEngine


@pytest.fixture(scope="session")
def input_documents() -> List[InputDocument]:
    return deprecated_load_input_documents_from_projects_json(
        os.path.join(
            os.path.dirname(__file__), "fixtures/deprecated_sample_projects.json"
        )
    )


@pytest.fixture(scope="session")
def application_summaries_by_ref(
    input_documents: List[InputDocument],
) -> Dict[str, ApplicationSummary]:
    application_summaries_by_ref: Dict[str, ApplicationSummary] = {}
    for input_document in input_documents:
        application_summaries_by_ref[
            input_document.document.metadata["application_ref"]
        ] = ApplicationSummary.from_metadata(input_document.document.metadata)
    return application_summaries_by_ref


@pytest.fixture(scope="session")
def search_engines(input_documents: List[InputDocument]) -> SearchEnginesFixture:
    fts_engine = FullTextSearchEngine()
    fts_index_filename = os.path.join(
        os.path.dirname(__file__), "fixtures/generated/fulltext_search_index.json"
    )
    if os.path.exists(fts_index_filename):
        fts_engine.load_index(fts_index_filename)
    else:
        fts_engine.index(input_documents)
        fts_engine.save_index(fts_index_filename)

    ss_engine = SemanticSearchEngine()
    semantic_index_filename = os.path.join(
        os.path.dirname(__file__), "fixtures/generated/semantic_index"
    )
    if os.path.exists(semantic_index_filename):
        ss_engine.load(semantic_index_filename)
    else:
        ss_engine.index(input_documents, persist_directory=semantic_index_filename)

    return SearchEnginesFixture(semantic=ss_engine, fulltext=fts_engine)


@pytest.fixture(scope="session")
def result_sets(search_engines: SearchEnginesFixture) -> SearchResultsFixture:
    fulltext_black_hare = search_engines.fulltext.search("black hare")
    fulltext_education = search_engines.fulltext.search("education")
    fulltext_nature_preservation = search_engines.fulltext.search("nature preservation")
    fulltext_blck_hare = search_engines.fulltext.search("blck hare")
    semantic_black_hare = search_engines.semantic.search("black hare")
    semantic_education = search_engines.semantic.search("education")
    semantic_nature_preservation = search_engines.semantic.search("nature preservation")
    semantic_blck_hare = search_engines.semantic.search("blck hare")

    return SearchResultsFixture(
        fulltext_black_hare=fulltext_black_hare,
        semantic_black_hare=semantic_black_hare,
        fulltext_education=fulltext_education,
        semantic_education=semantic_education,
        fulltext_nature_preservation=fulltext_nature_preservation,
        semantic_nature_preservation=semantic_nature_preservation,
        fulltext_blck_hare=fulltext_blck_hare,
        semantic_blck_hare=semantic_blck_hare,
    )
