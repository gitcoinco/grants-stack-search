import os
import time
import pickle
from os import path
import requests
import tempfile
import logging
from typing import Dict, List, Self, Any
from dataclasses import dataclass
from langchain.schema import Document
from langchain.document_loaders import JSONLoader, DirectoryLoader
from strip_markdown import strip_markdown
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
from src.search import ApplicationSummary
import json
from src.util import (
    ApplicationFileLocator,
    InputDocument,
    InvalidInputDocumentException,
    get_applications_file_url_from_application_file_locator,
    get_rounds_file_url_from_chain_id,
)


MAX_SUMMARY_TEXT_LENGTH = 300


def fetch_and_enrich_applications(
    applications_file_locators: List[ApplicationFileLocator],
    indexer_base_url: str,
) -> List[Any]:
    rounds_data_by_chain_id = {}

    def get_round_name(chain_id: int, round_id: str) -> str:
        if not chain_id in rounds_data_by_chain_id:
            rounds_file_url = get_rounds_file_url_from_chain_id(
                chain_id, indexer_base_url
            )
            response = requests.get(rounds_file_url)
            # TODO index by round id
            rounds_data_by_chain_id[chain_id] = json.loads(response.content)

        rounds_data = rounds_data_by_chain_id[chain_id]
        round = next(round for round in rounds_data if round["id"] == round_id)
        return round["metadata"]["name"]

    all_applications = []
    for applications_file_locator in applications_file_locators:
        applications_file_url = get_applications_file_url_from_application_file_locator(
            applications_file_locator, indexer_base_url
        )
        response = requests.get(applications_file_url)
        if response.status_code == 200:
            round_applications = json.loads(response.content)
            round_name = get_round_name(
                applications_file_locator.chain_id, applications_file_locator.round_id
            )
            for application in round_applications:
                application["chainId"] = applications_file_locator.chain_id
                application["roundName"] = round_name
            all_applications += round_applications
        else:
            logging.error(
                "Error fetching %s: %d", applications_file_url, response.status_code
            )
    return all_applications


def load_input_documents_from_file(
    applications_file_path: str, approved_applications_only: bool = True
) -> List[InputDocument]:
    jq_schema = ".[]"
    if approved_applications_only:
        jq_schema += ' | select(.status == "APPROVED")'
    jq_schema += " | { chain_id: .chainId, round_id: .roundId, round_name: .roundName, round_application_id: .id, project_id: .projectId, name: .metadata.application.project.title, payout_wallet_address: .metadata.application.recipient, website_url: .metadata.application.project.website, description: .metadata.application.project.description, banner_image_cid: .metadata.application.project.bannerImg, logo_image_cid: .metadata.application.project.logoImg, created_at_block: .createdAtBlock }"

    loader = JSONLoader(
        applications_file_path,
        jq_schema=jq_schema,
        content_key="description",
        metadata_func=get_application_json_document_metadata,
        text_content=False,
    )

    documents: List[InputDocument] = []
    for raw_document in loader.load():
        try:
            enrich_raw_document_with_computed_metadata(raw_document)
            documents.append(InputDocument(raw_document))
        except InvalidInputDocumentException:
            pass

    return documents


def get_application_json_document_metadata(record: dict, metadata: dict) -> dict:
    metadata["project_id"] = record.get("project_id")
    metadata["name"] = record.get("name")
    metadata["website_url"] = record.get("website_url")
    metadata["chain_id"] = record.get("chain_id")
    metadata["round_id"] = record.get("round_id")
    metadata["round_name"] = record.get("round_name")
    metadata["round_application_id"] = record.get("round_application_id")
    metadata["payout_wallet_address"] = record.get("payout_wallet_address")
    metadata["created_at_block"] = record.get("created_at_block")
    banner_image_cid = record.get("banner_image_cid")
    if banner_image_cid is not None:
        metadata["banner_image_cid"] = banner_image_cid
    logo_image_cid = record.get("logo_image_cid")
    if logo_image_cid is not None:
        metadata["logo_image_cid"] = logo_image_cid
    return metadata


def enrich_raw_document_with_computed_metadata(document: Document) -> None:
    chain_id = document.metadata["chain_id"]
    round_id = document.metadata["round_id"]
    round_application_id = document.metadata["round_application_id"]
    description_plain = strip_markdown(document.page_content)
    summary_text = description_plain[:MAX_SUMMARY_TEXT_LENGTH]
    if len(description_plain) > MAX_SUMMARY_TEXT_LENGTH:
        summary_text = summary_text + "..."
    document.metadata[
        "application_ref"
    ] = f"{chain_id}:{round_id}:{round_application_id}"
    document.metadata["round_application_id"] = round_application_id
    document.metadata["summary_text"] = summary_text


# Use a projects.json to generate input documents from. Fills in missing
# fields with dummy values. Legacy.
def deprecated_load_input_documents_from_projects_json(
    projects_json_path: str,
) -> List[InputDocument]:
    fake_application_counter = 0

    def get_json_document_metadata(record: dict, metadata: dict) -> dict:
        nonlocal fake_application_counter
        metadata["project_id"] = record.get("id")
        metadata["name"] = record.get("name")
        metadata["website_url"] = record.get("website_url")
        metadata["round_id"] = "0x123"
        metadata["round_application_id"] = str(fake_application_counter)
        metadata["chain_id"] = 1
        metadata["round_name"] = "Dummy Round Name"
        metadata["application_ref"] = f"1:0x123:{fake_application_counter}"
        metadata["payout_wallet_address"] = f"0xrecipient-{fake_application_counter}"
        metadata["created_at_block"] = 123456
        banner_image_cid = record.get("banner_image_cid")
        if banner_image_cid is not None:
            metadata["banner_image_cid"] = banner_image_cid
        logo_image_cid = record.get("logo_image_cid")
        if logo_image_cid is not None:
            metadata["logo_image_cid"] = logo_image_cid
        fake_application_counter = fake_application_counter + 1
        return metadata

    loader = JSONLoader(
        file_path=projects_json_path,
        jq_schema=".[] | { id, name: .metadata.title, website_url: .metadata.website, description: .metadata.description, banner_image_cid: .metadata.bannerImg, logo_image_cid: .metadata.logoImg }",
        content_key="description",
        metadata_func=get_json_document_metadata,
        text_content=False,
    )

    input_documents: List[InputDocument] = []
    for raw_document in loader.load():
        try:
            description_plain = strip_markdown(raw_document.page_content)
            summary_text = description_plain[:MAX_SUMMARY_TEXT_LENGTH]
            if len(description_plain) > MAX_SUMMARY_TEXT_LENGTH:
                summary_text = summary_text + "..."
            raw_document.metadata["summary_text"] = summary_text
            input_documents.append(InputDocument(raw_document))
        except InvalidInputDocumentException:
            pass

    return input_documents


@dataclass
class Data:
    application_summaries_by_ref: Dict[str, ApplicationSummary]
    fulltext_search_engine: FullTextSearchEngine
    semantic_search_engine: SemanticSearchEngine

    @classmethod
    def load(cls, storage_dir: str) -> Self:
        most_recent_run_dir = path.join(storage_dir, max(os.listdir(storage_dir)))

        with open(path.join(most_recent_run_dir, "applications.pkl"), "rb") as file:
            application_summaries_by_ref = pickle.load(file)

        semantic_search_engine = SemanticSearchEngine()
        semantic_search_engine.load(path.join(most_recent_run_dir, "chromadb"))

        fulltext_search_engine = FullTextSearchEngine()
        fulltext_search_engine.load_index(
            path.join(most_recent_run_dir, "fts-index.json")
        )

        return Data(
            fulltext_search_engine=fulltext_search_engine,
            semantic_search_engine=semantic_search_engine,
            application_summaries_by_ref=application_summaries_by_ref,
        )

    @classmethod
    def ingest_and_persist(
        cls,
        application_files_locators: List[ApplicationFileLocator],
        storage_dir: str,
        indexer_base_url: str,
    ) -> None:
        dir_for_this_run = path.join(storage_dir, str(int(time.time())))
        os.makedirs(dir_for_this_run, exist_ok=False)
        dataset_filename = path.join(dir_for_this_run, "applications_aggregate.json")

        with open(dataset_filename, "w") as f:
            json.dump(
                fetch_and_enrich_applications(
                    application_files_locators, indexer_base_url
                ),
                f,
                indent=2,
            )

        input_documents = load_input_documents_from_file(
            dataset_filename, approved_applications_only=False
        )

        application_summaries_by_ref: Dict[str, ApplicationSummary] = {}
        for input_document in input_documents:
            application_summaries_by_ref[
                input_document.document.metadata["application_ref"]
            ] = ApplicationSummary.from_metadata(input_document.document.metadata)

        semantic_search_engine = SemanticSearchEngine()
        semantic_search_engine.index(
            input_documents, persist_directory=path.join(dir_for_this_run, "chromadb")
        )

        fulltext_search_engine = FullTextSearchEngine()
        fulltext_search_engine.index(input_documents)

        fulltext_search_engine.save_index(path.join(dir_for_this_run, "fts-index.json"))

        with open(path.join(dir_for_this_run, "applications.pkl"), "wb") as file:
            pickle.dump(application_summaries_by_ref, file)
