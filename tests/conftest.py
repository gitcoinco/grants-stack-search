from dataclasses import dataclass
import pickle
import os
from typing import List, Literal, Union, Dict
from src.data import (
    InputDocument,
    deprecated_load_input_documents_from_projects_json,
)
import pytest
import logging

from src.search import (
    ApplicationSummary,
    SearchEngine,
    SearchEngineResult,
)
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


logging.basicConfig(level=logging.INFO)


SEARCH_RESULTS_FIXTURES_DIR = "tests/fixtures/search_results"
DEPRECATED_SAMPLE_PROJECTS_JSON_FILE = os.path.join(
    os.path.dirname(__file__), "fixtures/sample-projects.json"
)


@pytest.fixture(scope="session")
def input_documents() -> List[InputDocument]:
    return deprecated_load_input_documents_from_projects_json(
        DEPRECATED_SAMPLE_PROJECTS_JSON_FILE
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


@dataclass
class FixtureResultSets:
    fulltext_black_hare: List[SearchEngineResult]
    semantic_black_hare: List[SearchEngineResult]
    fulltext_education: List[SearchEngineResult]
    semantic_education: List[SearchEngineResult]
    fulltext_nature_preservation: List[SearchEngineResult]
    semantic_nature_preservation: List[SearchEngineResult]
    fulltext_blck_hare: List[SearchEngineResult]
    semantic_blck_hare: List[SearchEngineResult]


@pytest.fixture(scope="session")
def result_sets() -> FixtureResultSets:
    def generate_search_result_fixture(
        search_engine: SearchEngine, query: str
    ) -> List[SearchEngineResult]:
        search_type = search_engine.__class__.__name__.lower().replace(
            "searchengine", ""
        )
        query_filename_part = query.replace(" ", "_")
        fixture_filename = (
            f"{SEARCH_RESULTS_FIXTURES_DIR}/{search_type}_{query_filename_part}.pickle"
        )

        os.makedirs(SEARCH_RESULTS_FIXTURES_DIR, exist_ok=True)
        results = search_engine.search(query)
        with open(fixture_filename, "wb") as file:
            pickle.dump(results, file)
        return results

    def load_search_result_fixture(
        search_type: Union[Literal["fulltext"], Literal["semantic"]], query: str
    ) -> List[SearchEngineResult]:
        query_filename_part = query.replace(" ", "_")
        fixture_filename = (
            f"{SEARCH_RESULTS_FIXTURES_DIR}/{search_type}_{query_filename_part}.pickle"
        )
        with open(fixture_filename, "rb") as file:
            return pickle.load(file)

    if os.path.isdir(SEARCH_RESULTS_FIXTURES_DIR):
        return FixtureResultSets(
            fulltext_black_hare=load_search_result_fixture(
                search_type="fulltext", query="black hare"
            ),
            semantic_black_hare=load_search_result_fixture(
                search_type="semantic", query="black hare"
            ),
            fulltext_education=load_search_result_fixture(
                search_type="fulltext", query="education"
            ),
            semantic_education=load_search_result_fixture(
                search_type="semantic", query="education"
            ),
            fulltext_nature_preservation=load_search_result_fixture(
                search_type="fulltext", query="nature preservation"
            ),
            semantic_nature_preservation=load_search_result_fixture(
                search_type="semantic", query="nature preservation"
            ),
            fulltext_blck_hare=load_search_result_fixture(
                search_type="fulltext", query="blck hare"
            ),
            semantic_blck_hare=load_search_result_fixture(
                search_type="semantic", query="blck hare"
            ),
        )
    else:
        project_docs = deprecated_load_input_documents_from_projects_json(
            DEPRECATED_SAMPLE_PROJECTS_JSON_FILE
        )
        fts_engine = FullTextSearchEngine()
        fts_engine.index(project_docs)
        ss_engine = SemanticSearchEngine()
        ss_engine.index(project_docs)

        return FixtureResultSets(
            fulltext_black_hare=generate_search_result_fixture(
                search_engine=fts_engine, query="black hare"
            ),
            semantic_black_hare=generate_search_result_fixture(
                search_engine=ss_engine, query="black hare"
            ),
            fulltext_education=generate_search_result_fixture(
                search_engine=fts_engine, query="education"
            ),
            semantic_education=generate_search_result_fixture(
                search_engine=ss_engine, query="education"
            ),
            fulltext_nature_preservation=generate_search_result_fixture(
                search_engine=fts_engine, query="nature preservation"
            ),
            semantic_nature_preservation=generate_search_result_fixture(
                search_engine=ss_engine, query="nature preservation"
            ),
            fulltext_blck_hare=generate_search_result_fixture(
                search_engine=fts_engine, query="blck hare"
            ),
            semantic_blck_hare=generate_search_result_fixture(
                search_engine=ss_engine, query="blck hare"
            ),
        )
