from typing import List
from langchain.schema import Document
from langchain.document_loaders import JSONLoader


class InvalidInputProjectDocumentException(Exception):
    pass


# Wrap a Document to carry validity information together with the type
class InputProjectDocument:
    def __init__(self, document: Document):
        if (
            # TODO use pydantic already here?
            isinstance(document.metadata.get("project_id"), str)
            and isinstance(document.metadata.get("name"), str)
            and isinstance(document.metadata.get("website_url"), str)
            and document.page_content is not None
        ):
            self.document = document
        else:
            raise InvalidInputProjectDocumentException(
                document.metadata.get("project_id")
            )


def load_projects_json(projects_json_path: str) -> List[InputProjectDocument]:
    loader = JSONLoader(
        file_path=projects_json_path,
        jq_schema=".[] | { id, name: .metadata.title, website_url: .metadata.website, description: .metadata.description, banner_image_cid: .metadata.bannerImg }",
        content_key="description",
        metadata_func=get_json_document_metadata,
        text_content=False,
    )

    documents: List[InputProjectDocument] = []
    for generic_document in loader.load():
        try:
            documents.append(InputProjectDocument(generic_document))
        except InvalidInputProjectDocumentException:
            pass

    return documents


def get_json_document_metadata(record: dict, metadata: dict) -> dict:
    metadata["project_id"] = record.get("id")
    metadata["name"] = record.get("name")
    metadata["website_url"] = record.get("website_url")
    banner_image_cid = record.get("banner_image_cid")
    if banner_image_cid is not None:
        metadata["banner_image_cid"] = banner_image_cid
    return metadata
