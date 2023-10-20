from dataclasses import dataclass
import pickle
import os
from typing import List, Dict, TypedDict, Literal, Union
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from src.data import (
    InputProjectDocument,
    load_project_dataset_into_vectorstore,
    load_project_dataset_into_chroma_db,
    get_qa_chain,
    load_projects_json,
)
import pytest
import logging

from src.search import SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


logging.basicConfig(level=logging.DEBUG)


SAMPLE_PROJECTS_JSON_FILE = os.path.join(
    os.path.dirname(__file__), "fixtures/sample-projects.json"
)


@pytest.fixture(scope="session")
def qa_chain() -> BaseRetrievalQA:
    return get_qa_chain(SAMPLE_PROJECTS_JSON_FILE)


@pytest.fixture(scope="session")
def chroma_db() -> Chroma:
    return load_project_dataset_into_chroma_db(SAMPLE_PROJECTS_JSON_FILE)


@pytest.fixture(scope="session")
def vector_store_index() -> VectorStoreIndexWrapper:
    return load_project_dataset_into_vectorstore(SAMPLE_PROJECTS_JSON_FILE)


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
    # To create a fixture:
    #
    # project_docs = load_projects_json(PROJECTS_JSON_FILE)
    # fts_engine = FullTextSearchEngine()
    # fts_engine.index_projects(project_docs)
    # with open(
    #     "tests/fixtures/search_results_semantic_nature_preservation.pickle", "wb"
    # ) as file:
    #     pickle.dump(ss_engine.search("nature preservation"), file)

    # project_docs = load_projects_json(".var/1/projects.json")
    # fts_engine = FullTextSearchEngine()
    # fts_engine.index_projects(project_docs)
    # ss_engine = SemanticSearchEngine()
    # ss_engine.index_projects(project_docs)

    # with open("tests/fixtures/search_results_fulltext_blck_hare.pickle", "wb") as file:
    #     pickle.dump(fts_engine.search("blck hare"), file)

    # with open("tests/fixtures/search_results_semantic_blck_hare.pickle", "wb") as file:
    #     pickle.dump(ss_engine.search("blck hare"), file)

    with open("tests/fixtures/search_results_fulltext_black_hare.pickle", "rb") as file:
        fulltext_results_black_hare = pickle.load(file)

    with open("tests/fixtures/search_results_semantic_black_hare.pickle", "rb") as file:
        semantic_results_black_hare = pickle.load(file)

    with open("tests/fixtures/search_results_fulltext_education.pickle", "rb") as file:
        fulltext_results_education = pickle.load(file)

    with open("tests/fixtures/search_results_semantic_education.pickle", "rb") as file:
        semantic_results_education = pickle.load(file)

    with open(
        "tests/fixtures/search_results_fulltext_nature_preservation.pickle", "rb"
    ) as file:
        fulltext_results_nature_preservation = pickle.load(file)

    with open(
        "tests/fixtures/search_results_semantic_nature_preservation.pickle", "rb"
    ) as file:
        semantic_results_nature_preservation = pickle.load(file)

    with open("tests/fixtures/search_results_fulltext_blck_hare.pickle", "rb") as file:
        fulltext_results_blck_hare = pickle.load(file)

    with open("tests/fixtures/search_results_semantic_blck_hare.pickle", "rb") as file:
        semantic_results_blck_hare = pickle.load(file)

    return ResultSets(
        fulltext_black_hare=fulltext_results_black_hare,
        semantic_black_hare=semantic_results_black_hare,
        fulltext_education=fulltext_results_education,
        semantic_education=semantic_results_education,
        fulltext_nature_preservation=fulltext_results_nature_preservation,
        semantic_nature_preservation=semantic_results_nature_preservation,
        fulltext_blck_hare=fulltext_results_blck_hare,
        semantic_blck_hare=semantic_results_blck_hare,
    )
