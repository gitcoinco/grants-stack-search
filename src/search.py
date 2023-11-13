from dataclasses import dataclass
from enum import Enum
from typing import List, Any
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from src.util import InputDocument


class SearchType(str, Enum):
    fulltext = "fulltext"
    semantic = "semantic"


class SearchResultMeta(BaseModel):
    search_type: SearchType = Field(serialization_alias="searchType")
    search_score: float = Field(serialization_alias="searchScore")


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
