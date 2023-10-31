from typing import List
from langchain.schema import Document
from langchain.document_loaders import JSONLoader, DirectoryLoader


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


def load_applications_dir(
    applications_dir_path: str, filter_duplicate_projects=True
) -> List[InputProjectDocument]:
    loader = DirectoryLoader(
        applications_dir_path,
        glob="*.json",
        show_progress=True,
        loader_cls=JSONLoader,  # type: ignore -- typings seem to require an UnstructuredLoader
        loader_kwargs={
            "jq_schema": ".[] | { id: .projectId, name: .metadata.application.project.title, website_url: .metadata.application.project.website, description: .metadata.application.project.description, banner_image_cid: .metadata.application.project.bannerImg }",
            "content_key": "description",
            "metadata_func": get_json_document_metadata,
            "text_content": False,
        },
    )

    already_loaded_projects = {}

    documents: List[InputProjectDocument] = []
    for generic_document in loader.load():
        try:
            input_document = InputProjectDocument(generic_document)
            project_id = input_document.document.metadata.get("project_id")
            if (
                filter_duplicate_projects
                and already_loaded_projects.get(project_id, False) == True
            ):
                pass
            else:
                documents.append(input_document)
                already_loaded_projects[project_id] = True
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
