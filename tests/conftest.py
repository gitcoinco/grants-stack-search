import os
from typing import List
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
