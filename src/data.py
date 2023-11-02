from typing import List, Dict
from langchain.schema import Document
from langchain.document_loaders import JSONLoader, DirectoryLoader


class InvalidInputDocumentException(Exception):
    pass


# Wrap a Document to carry validity information together with the type
class InputDocument:
    def __init__(self, document: Document):
        if (
            isinstance(document.metadata.get("application_ref"), str)
            and isinstance(document.metadata.get("name"), str)
            and isinstance(document.metadata.get("website_url"), str)
            and isinstance(document.metadata.get("round_id"), str)
            and isinstance(document.metadata.get("chain_id"), int)
            and isinstance(document.metadata.get("round_application_id"), str)
            # banner_image_cid and logo_image_cid are optional
            and document.page_content is not None
        ):
            self.document = document
        else:
            raise InvalidInputDocumentException(
                document.metadata.get("application_ref")
            )


# Uses a projects.json to generate input documents from. Fills in missing
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
        metadata["application_ref"] = f"1:0x123:{fake_application_counter}"
        banner_image_cid = record.get("banner_image_cid")
        if banner_image_cid is not None:
            metadata["banner_image_cid"] = banner_image_cid
        fake_application_counter = fake_application_counter + 1
        return metadata

    loader = JSONLoader(
        file_path=projects_json_path,
        jq_schema=".[] | { id, name: .metadata.title, website_url: .metadata.website, description: .metadata.description, banner_image_cid: .metadata.bannerImg }",
        content_key="description",
        metadata_func=get_json_document_metadata,
        text_content=False,
    )

    input_documents: List[InputDocument] = []
    for raw_document in loader.load():
        try:
            input_documents.append(InputDocument(raw_document))
        except InvalidInputDocumentException:
            pass

    return input_documents


def load_input_documents_from_data(_data: List[Dict]) -> List[InputDocument]:
    raise Exception("Not implemented")


def load_input_documents_from_applications_dir(
    applications_dir_path: str, chain_id: int
) -> List[InputDocument]:
    loader = DirectoryLoader(
        applications_dir_path,
        glob="*.json",
        show_progress=True,
        loader_cls=JSONLoader,  # type: ignore -- typings seem to require an UnstructuredLoader
        loader_kwargs={
            "jq_schema": ".[] | { round_id: .roundId, round_application_id: .id, project_id: .projectId, name: .metadata.application.project.title, website_url: .metadata.application.project.website, description: .metadata.application.project.description, banner_image_cid: .metadata.application.project.bannerImg }",
            "content_key": "description",
            "metadata_func": get_json_document_metadata,
            "text_content": False,
        },
    )

    documents: List[InputDocument] = []
    for generic_document in loader.load():
        try:
            round_id = generic_document.metadata["round_id"]
            round_application_id = generic_document.metadata["round_application_id"]
            generic_document.metadata[
                "application_ref"
            ] = f"{chain_id}:{round_id}:{round_application_id}"
            generic_document.metadata["chain_id"] = chain_id
            generic_document.metadata["round_application_id"] = round_application_id
            documents.append(InputDocument(generic_document))
        except InvalidInputDocumentException:
            pass

    return documents


def get_json_document_metadata(record: dict, metadata: dict) -> dict:
    metadata["project_id"] = record.get("project_id")
    metadata["name"] = record.get("name")
    metadata["website_url"] = record.get("website_url")
    metadata["round_id"] = record.get("round_id")
    metadata["round_application_id"] = record.get("round_application_id")
    banner_image_cid = record.get("banner_image_cid")
    if banner_image_cid is not None:
        metadata["banner_image_cid"] = banner_image_cid
    return metadata
