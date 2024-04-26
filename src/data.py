import time
import shutil
import os
import pickle
from os import path
import requests
import logging
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Self
from langchain.schema import Document
from langchain.document_loaders import JSONLoader
from strip_markdown import strip_markdown
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
import json
from src.util import (
    ApplicationFileLocator,
    InputDocument,
    InvalidInputDocumentException,
    get_applications_file_url_from_application_file_locator,
    get_rounds_file_url_from_chain_id,
)

# TODO lift to configuration
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
        metadata["contributor_count"] = record.get("contributor_count")
        metadata["contributions_total_usd"] = record.get("contributions_total_usd")
        metadata["anchor_address"] = record.get("anchor_address")

        banner_image_cid = record.get("banner_image_cid")
        if banner_image_cid is not None:
            metadata["banner_image_cid"] = banner_image_cid
        logo_image_cid = record.get("logo_image_cid")
        if logo_image_cid is not None:
            metadata["logo_image_cid"] = logo_image_cid
        return metadata

    jq_schema = ".[]"
    if approved_applications_only:
        jq_schema += ' | select(.status == "APPROVED")'
    jq_schema += " | { chain_id: .chainId, round_id: .roundId, round_name: .roundName, round_application_id: .id, project_id: .projectId, name: .metadata.application.project.title, payout_wallet_address: .metadata.application.recipient, website_url: .metadata.application.project.website, description: .metadata.application.project.description, banner_image_cid: .metadata.application.project.bannerImg, logo_image_cid: .metadata.application.project.logoImg, created_at_block: .createdAtBlock, contributions_total_usd: .amountUSD, contributor_count: .uniqueContributors, anchor_address: .anchorAddress}"

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
        metadata["contributor_count"] = 1
        metadata["contributions_total_usd"] = 100
        metadata["anchor_address"] = "0x123"
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
        jq_schema=".[] | { id, name: .metadata.title, website_url: .metadata.website, description: .metadata.description, banner_image_cid: .metadata.bannerImg, logo_image_cid: .metadata.logoImg, anchor_address: .anchorAddress}",
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


class ApplicationSummary(BaseModel):
    application_ref: str = Field(serialization_alias="applicationRef")
    chain_id: int = Field(serialization_alias="chainId")
    round_application_id: str = Field(serialization_alias="roundApplicationId")
    round_id: str = Field(serialization_alias="roundId")
    round_name: str = Field(serialization_alias="roundName")
    project_id: str = Field(serialization_alias="projectId")
    name: str = Field(serialization_alias="name")
    website_url: str = Field(serialization_alias="websiteUrl")
    logo_image_cid: str | None = Field(serialization_alias="logoImageCid")
    banner_image_cid: str | None = Field(serialization_alias="bannerImageCid")
    summary_text: str = Field(serialization_alias="summaryText")
    payout_wallet_address: str = Field(serialization_alias="payoutWalletAddress")
    created_at_block: int = Field(serialization_alias="createdAtBlock")
    contributor_count: int = Field(serialization_alias="contributorCount")
    contributions_total_usd: float = Field(serialization_alias="contributionsTotalUsd")
    anchor_address: str = Field(serialization_alias="anchorAddress")

    @classmethod
    def from_metadata(cls, metadata: Any) -> Self:
        return cls(
            application_ref=metadata.get("application_ref"),
            round_id=metadata.get("round_id"),
            round_name=metadata.get("round_name"),
            round_application_id=metadata.get("round_application_id"),
            chain_id=metadata.get("chain_id"),
            project_id=metadata.get("project_id"),
            name=metadata.get("name"),
            website_url=metadata.get("website_url"),
            logo_image_cid=metadata.get("logo_image_cid"),
            banner_image_cid=metadata.get("banner_image_cid"),
            summary_text=metadata.get("summary_text"),
            payout_wallet_address=metadata.get("payout_wallet_address"),
            created_at_block=metadata.get("created_at_block"),
            contributor_count=metadata.get("contributor_count"),
            contributions_total_usd=metadata.get("contributions_total_usd"),
            anchor_address=metadata.get("anchor_address"),
        )


class Data:
    """
    Convenience aggregation of all the data the service is meant to use during operation.
    """

    # TODO add properties that return applications and search engines
    # but raise if they have not been initialized (i.e. if `reload` has not)
    # been called after instantiation

    application_summaries_by_ref: Dict[str, ApplicationSummary]
    fulltext_search_engine: FullTextSearchEngine
    semantic_search_engine: SemanticSearchEngine

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir

    # TODO test
    def reload(self):
        # Only application data is reloaded because indices are
        # currently only built once on service startup.

        with open(path.join(self.storage_dir, "applications.pkl"), "rb") as file:
            applications = pickle.load(file)
            if not hasattr(self, "application_summaries_by_ref"):
                self.application_summaries_by_ref = applications
            else:
                if len(applications) == 0:
                    logging.warn(
                        "Anomaly detected: freshly reloaded applications is zero. Not replacing data set.",
                        len(self.application_summaries_by_ref),
                        len(applications),
                    )
                else:
                    self.application_summaries_by_ref = applications

        if not hasattr(self, "fulltext_search_engine"):
            self.fulltext_search_engine = FullTextSearchEngine()
            self.fulltext_search_engine.load_index(
                path.join(self.storage_dir, "fulltext_search_index.json")
            )

        if not hasattr(self, "semantic_search_engine"):
            self.semantic_search_engine = SemanticSearchEngine()
            self.semantic_search_engine.load(path.join(self.storage_dir, "chromadb"))

    @classmethod
    # TODO test
    def ingest_from_application_locators_and_persist(
        cls,
        application_files_locators: List[ApplicationFileLocator],
        storage_dir: str,
        indexer_base_url: str,
        first_run: bool,
    ) -> None:
        if first_run and os.path.exists(storage_dir):
            logging.info(f"Clearing {storage_dir}...")
            shutil.rmtree(storage_dir)

        os.makedirs(storage_dir, exist_ok=True)

        source_dataset_filename = path.join(storage_dir, "applications_aggregate.json")

        with open(source_dataset_filename, "w") as f:
            aggregated_applications = fetch_and_enrich_applications(
                application_files_locators,
                indexer_base_url,
            )
            aggregated_applications[0]["projectId"] = str(int(time.time()))
            json.dump(aggregated_applications, f, indent=2)

        cls.ingest_from_file_and_persist(
            source_dataset_filename=source_dataset_filename,
            storage_dir=storage_dir,
            first_run=first_run,
        )

    @classmethod
    def ingest_from_file_and_persist(
        cls, source_dataset_filename: str, storage_dir: str, first_run: bool
    ) -> None:
        applications_filename = path.join(storage_dir, "applications.pkl")
        fulltext_index_filename = path.join(storage_dir, "fulltext_search_index.json")
        semantic_index_dirname = path.join(storage_dir, "chromadb")

        input_documents = load_input_documents_from_file(
            source_dataset_filename, approved_applications_only=True
        )

        application_summaries_by_ref: Dict[str, ApplicationSummary] = {}
        for input_document in input_documents:
            application_summaries_by_ref[
                input_document.document.metadata["application_ref"]
            ] = ApplicationSummary.from_metadata(input_document.document.metadata)

        with open(applications_filename + ".tmp", "wb") as file:
            pickle.dump(application_summaries_by_ref, file)
        os.rename(applications_filename + ".tmp", applications_filename)

        if first_run:
            if os.path.exists(fulltext_index_filename) or os.path.exists(
                semantic_index_dirname
            ):
                raise Exception(
                    "Reindexing not yet supported. Remove old indices before restarting service."
                )

            semantic_search_engine = SemanticSearchEngine()
            semantic_search_engine.index(
                input_documents, persist_directory=semantic_index_dirname
            )

            fulltext_search_engine = FullTextSearchEngine()
            fulltext_search_engine.index(input_documents)
            fulltext_search_engine.save_index(fulltext_index_filename)
