import json
import time
import logging
from lunr import lunr
from lunr.index import Index
from typing import List
from src.util import InputDocument
from src.search import SearchEngine, SearchEngineResult, SearchType


class FullTextSearchEngine(SearchEngine):
    def index(self, input_documents: List[InputDocument]) -> None:
        start_time = time.perf_counter()

        self.search_index = lunr(
            ref="application_ref",
            fields=[
                dict(field_name="name", boost=10),
                "description",
                "website_url",
            ],
            documents=[
                dict(
                    application_ref=i.document.metadata["application_ref"],
                    name=i.document.metadata["name"],
                    description=i.document.page_content,
                    website_url=i.document.metadata["website_url"],
                )
                for i in input_documents
            ],
        )
        logging.debug(
            "indexed %d projects in %.2f seconds with lunr.py",
            len(input_documents),
            time.perf_counter() - start_time,
        )

    def search(self, query_string: str) -> List[SearchEngineResult]:
        return [
            SearchEngineResult(ref=r["ref"], score=r["score"], type=SearchType.fulltext)
            for r in self.search_index.search(query_string)
        ]

    def save_index(self, path: str) -> None:
        with open(path, "w") as file:
            json.dump(self.search_index.serialize(), file)

    def load_index(self, path: str) -> None:
        with open(path) as file:
            serialized_index = json.loads(file.read())
            self.search_index = Index.load(serialized_index)
