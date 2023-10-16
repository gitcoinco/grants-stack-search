from typing import List
from abc import ABC, abstractmethod
from src.data import InputProjectDocument


class SearchEngine(ABC):
    @abstractmethod
    def index_projects(self, project_docs: List[InputProjectDocument]) -> None:
        pass

    @abstractmethod
    def search(self, query_string: str) -> List[InputProjectDocument]:
        pass
