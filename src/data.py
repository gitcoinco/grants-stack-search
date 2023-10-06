import logging
import os
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import JSONLoader
from langchain.chains import RetrievalQA
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.llms import OpenAI
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.document_loaders import JSONLoader
from langchain.indexes import VectorstoreIndexCreator


JQ_SCHEMA = ".[] | { id, name: .metadata.title, website_url: .metadata.website, description: .metadata.description, banner_image_cid: .metadata.bannerImg }"


def get_json_document_metadata(record: dict, metadata: dict) -> dict:
    metadata["project_id"] = record.get("id")
    metadata["name"] = record.get("name")
    metadata["website_url"] = record.get("website_url")
    banner_image_cid = record.get("banner_image_cid")
    if banner_image_cid is not None:
        metadata["banner_image_cid"] = banner_image_cid
    return metadata


def load_project_dataset_into_chroma_db(projects_file_path: str) -> Chroma:
    loader = JSONLoader(
        file_path=projects_file_path,
        jq_schema=JQ_SCHEMA,
        content_key="description",
        metadata_func=get_json_document_metadata,
        text_content=False,
    )
    logging.debug(f"loading {os.path.basename(projects_file_path)}...")
    documents = loader.load()

    logging.debug("indexing...")
    db = Chroma.from_documents(
        documents=documents,
        embedding=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
        ids=[doc.metadata["project_id"] for doc in documents],
    )
    return db


def load_project_dataset_into_vectorstore(
    projects_file_path: str,
) -> VectorStoreIndexWrapper:
    loader = JSONLoader(
        file_path=projects_file_path,
        jq_schema=JQ_SCHEMA,
        content_key="description",
        metadata_func=get_json_document_metadata,
        text_content=False,
    )
    logging.debug(f"loading {os.path.basename(projects_file_path)}...")

    index = VectorstoreIndexCreator().from_loaders([loader])

    return index


def get_qa_chain(project_file_path: str) -> BaseRetrievalQA:
    logging.debug(f"creating index from {project_file_path} ...")
    index = VectorstoreIndexCreator().from_loaders(
        [
            JSONLoader(
                file_path=project_file_path,
                jq_schema=JQ_SCHEMA,
                content_key="description",
                metadata_func=get_json_document_metadata,
            )
        ]
    )

    logging.debug("constructing qa chain")
    chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=index.vectorstore.as_retriever(),
        input_key="question",
    )

    return chain
