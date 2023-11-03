from typing import ClassVar, List, Any, Literal, Self, Union
from pydantic import BaseModel, computed_field
from abc import ABC, abstractmethod
from src.data import InputDocument
from urllib.parse import urljoin


class SearchResultMeta(BaseModel):
    search_type: Union[Literal["fulltext"], Literal["semantic"]]
    search_score: float


class ApplicationSummary(BaseModel):
    # TODO alias to camelCase, e.g.
    # foo_bar: str = Field(alias='fooBar')
    application_ref: str
    chain_id: int
    round_application_id: str
    round_id: str
    project_id: str
    name: str
    website_url: str
    banner_image_cid: str | None
    summary_text: str

    @computed_field
    @property
    def banner_image_url(self) -> str | None:
        if self.banner_image_cid is None:
            return None
        else:
            return urljoin(
                SearchResult.IPFS_GATEWAY_BASE, "ipfs/" + self.banner_image_cid
            )

    @classmethod
    def from_metadata(cls, metadata: Any) -> Self:
        return cls(
            application_ref=metadata.get("application_ref"),
            round_id=metadata.get("round_id"),
            round_application_id=metadata.get("round_application_id"),
            chain_id=metadata.get("chain_id"),
            project_id=metadata.get("project_id"),
            name=metadata.get("name"),
            website_url=metadata.get("website_url"),
            banner_image_cid=metadata.get("banner_image_cid"),
            summary_text=metadata.get("summary_text"),
        )


class SearchResult(BaseModel):
    meta: SearchResultMeta
    data: ApplicationSummary

    IPFS_GATEWAY_BASE: ClassVar[str] = "https://ipfs.io"

    @classmethod
    def from_content_and_metadata(
        cls,
        content: Any,
        metadata: Any,
        search_score: float,
        search_type: Union[Literal["fulltext"], Literal["semantic"]],
    ) -> Self:
        return cls(
            data=ApplicationSummary.from_metadata(metadata),
            meta=SearchResultMeta(search_score=search_score, search_type=search_type),
        )

    @classmethod
    def from_input_document(
        cls,
        input_document: InputDocument,
        search_score: float,
        search_type: Union[Literal["fulltext"], Literal["semantic"]],
    ) -> Self:
        metadata = input_document.document.metadata
        content = input_document.document.page_content
        return cls.from_content_and_metadata(
            content, metadata, search_score=search_score, search_type=search_type
        )


class SearchEngine(ABC):
    @abstractmethod
    def index(self, project_docs: List[InputDocument]) -> None:
        pass

    @abstractmethod
    def search(self, query_string: str) -> List[SearchResult]:
        pass


def assert_str(value: Any) -> str:
    if not isinstance(value, str):
        raise Exception("Not a string")
    return value
