from langchain.document_loaders import JSONLoader
from rake_nltk import Rake
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
import pytest
import rich
import nltk
from langchain.vectorstores import Chroma
from pprint import pprint


# NOTE: these are not real tests, we're using pytest as a testbed.


@pytest.mark.skip
def test_experiment_similarity_search_with_chroma_db(chroma_db: Chroma):
    query = "education"
    docs = chroma_db.similarity_search(query)

    print("EDUCATION:")
    for doc in docs[0:5]:
        print(" - ", doc.metadata["name"])

    query = "market-making"
    docs = chroma_db.similarity_search(query)

    print("MARKET MAKING: ")
    for doc in docs[0:5]:
        print(" - ", doc.metadata["name"])


@pytest.mark.skip
def test_experiment_qa_with_vector_store_index(
    vector_store_index: VectorStoreIndexWrapper,
):
    query = "which projects relate to education?"
    answer = vector_store_index.query_with_sources(query)
    rich.print(answer)


@pytest.mark.skip
def test_experiment_qa_with_chain(qa_chain: BaseRetrievalQA):
    question = "which projects relate to education?"
    response = qa_chain({"question": question})
    rich.print(response)


@pytest.mark.skip
def test_experiment_keyword_extraction_with_rake():
    nltk.download("stopwords")
    nltk.download("punkt")

    def get_metadata(record: dict, metadata: dict) -> dict:
        metadata["name"] = record.get("title")
        metadata["website_url"] = record.get("website")
        return metadata

    loader = JSONLoader(
        file_path=".var/1/projects.shortened.json",
        jq_schema=".[].metadata | { title, website, description }",
        content_key="description",
        metadata_func=get_metadata,
        text_content=False,
    )

    docs = loader.load()
    docs_with_title = [d.metadata["name"] + "\n\n" + d.page_content for d in docs]
    text = "\n\n".join(docs_with_title)
    r = Rake()
    r.extract_keywords_from_text(text)
    pprint(r.get_ranked_phrases_with_scores()[0:30])
