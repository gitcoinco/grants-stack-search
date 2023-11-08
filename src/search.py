from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Self
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from src.util import InputDocument


class SearchType(str, Enum):
    fulltext = "fulltext"
    semantic = "semantic"


class SearchResultMeta(BaseModel):
    search_type: SearchType = Field(serialization_alias="searchType")
    search_score: float = Field(serialization_alias="searchScore")


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
        )


@dataclass
class SearchEngineResult:
    ref: str
    score: float
    type: SearchType


class SearchEngine(ABC):
    @abstractmethod
    def index(self, project_docs: List[InputDocument]) -> None:
        pass

    @abstractmethod
    def search(self, query_string: str) -> List[SearchEngineResult]:
        pass


def assert_str(value: Any) -> str:
    if not isinstance(value, str):
        raise Exception("Not a string")
    return value
