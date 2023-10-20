from mdx_linkify import mdx_linkify
from typing import ClassVar, List, Any, Self
from pydantic import BaseModel, computed_field
from abc import ABC, abstractmethod
from src.data import InputProjectDocument
from strip_markdown import strip_markdown
from markdown import markdown
from urllib.parse import urljoin

markdown_linkify_extension = mdx_linkify.LinkifyExtension()


# TODO defining this after `SearchEngine` causes "variable not defined" type warning in the definition of `search`. can it be avoided?
class SearchResult(BaseModel):
    project_id: str
    name: str
    description_markdown: str
    website_url: str
    banner_image_cid: str | None
    score: float

    IPFS_GATEWAY_BASE: ClassVar[str] = "https://ipfs.io"

    @classmethod
    def from_content_and_metadata(
        cls, content: Any, metadata: Any, score: float
    ) -> Self:
        return cls(
            project_id=metadata.get("project_id"),
            name=metadata.get("name"),
            description_markdown=content,
            website_url=metadata.get("website_url"),
            banner_image_cid=metadata.get("banner_image_cid"),
            score=score,
        )

    @classmethod
    def from_input_document(
        cls, input_document: InputProjectDocument, score: float
    ) -> Self:
        metadata = input_document.document.metadata
        content = input_document.document.page_content
        return cls.from_content_and_metadata(content, metadata, score)

    @computed_field
    @property
    def description_plain(self) -> str:
        return strip_markdown(self.description_markdown)

    @computed_field
    @property
    def description_html(self) -> str:
        return markdown(
            self.description_markdown, extensions=[markdown_linkify_extension]
        )

    @computed_field
    @property
    def banner_image_url(self) -> str | None:
        if self.banner_image_cid is None:
            return None
        else:
            return urljoin(
                SearchResult.IPFS_GATEWAY_BASE, "ipfs/" + self.banner_image_cid
            )


class SearchEngine(ABC):
    @abstractmethod
    def index_projects(self, project_docs: List[InputProjectDocument]) -> None:
        pass

    @abstractmethod
    def search(self, query_string: str) -> List[SearchResult]:
        pass


def assert_str(value: Any) -> str:
    if not isinstance(value, str):
        raise Exception("Not a string")
    return value
