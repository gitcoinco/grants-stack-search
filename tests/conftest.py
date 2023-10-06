from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from src.data import (
    load_project_dataset_into_vectorstore,
    load_project_dataset_into_chroma_db,
    get_qa_chain,
)
from dotenv import load_dotenv
import pytest

load_dotenv()

DATA_FILE = ".var/1/projects.shortened.json"


@pytest.fixture(scope="session")
def qa_chain() -> BaseRetrievalQA:
    return get_qa_chain(DATA_FILE)


@pytest.fixture(scope="session")
def chroma_db() -> Chroma:
    return load_project_dataset_into_chroma_db(DATA_FILE)


@pytest.fixture(scope="session")
def vector_store_index() -> VectorStoreIndexWrapper:
    return load_project_dataset_into_vectorstore(DATA_FILE)
