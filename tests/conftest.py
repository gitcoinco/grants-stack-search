from dataclasses import dataclass
import pickle
import os
from typing import List, Literal, Union
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from src.data import (
    InputProjectDocument,
    load_projects_json,
)
import pytest
import logging

from src.search import SearchEngine, SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


logging.basicConfig(level=logging.INFO)


SEARCH_RESULTS_FIXTURES_DIR = "tests/fixtures/search_results"
# TODO: change to reflect the fact that we now process applications files instead of projects file
SAMPLE_PROJECTS_JSON_FILE = os.path.join(
    os.path.dirname(__file__), "fixtures/sample-projects.json"
)


@pytest.fixture(scope="session")
def project_docs() -> List[InputProjectDocument]:
    return load_projects_json(SAMPLE_PROJECTS_JSON_FILE)


@dataclass
class ResultSets:
    fulltext_black_hare: List[SearchResult]
    semantic_black_hare: List[SearchResult]
    fulltext_education: List[SearchResult]
    semantic_education: List[SearchResult]
    fulltext_nature_preservation: List[SearchResult]
    semantic_nature_preservation: List[SearchResult]
    fulltext_blck_hare: List[SearchResult]
    semantic_blck_hare: List[SearchResult]


@pytest.fixture(scope="session")
def result_sets() -> ResultSets:
    def generate_search_result_fixture(
        search_engine: SearchEngine, query: str
    ) -> List[SearchResult]:
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
    ) -> List[SearchResult]:
        query_filename_part = query.replace(" ", "_")
        fixture_filename = (
            f"{SEARCH_RESULTS_FIXTURES_DIR}/{search_type}_{query_filename_part}.pickle"
        )
        with open(fixture_filename, "rb") as file:
            return pickle.load(file)

    if os.path.isdir(SEARCH_RESULTS_FIXTURES_DIR):
        return ResultSets(
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
        project_docs = load_projects_json(SAMPLE_PROJECTS_JSON_FILE)
        fts_engine = FullTextSearchEngine()
        fts_engine.index_projects(project_docs)
        ss_engine = SemanticSearchEngine()
        ss_engine.index_projects(project_docs)

        return ResultSets(
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
