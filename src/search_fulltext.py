import time
import logging
from lunr import lunr
from typing import List
from src.data import InputDocument
from src.search import SearchEngine, SearchResult


class FullTextSearchEngine(SearchEngine):
    def index(self, input_documents: List[InputDocument]) -> None:
        start_time = time.perf_counter()
        self.document_index = {
            # TODO application_ref needs test
            i.document.metadata["application_ref"]: i
            for i in input_documents
        }

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

    def search(self, query_string: str) -> List[SearchResult]:
        return [
            SearchResult.from_input_document(
                input_document=self.document_index[raw_result["ref"]],
                search_score=raw_result["score"],
                search_type="fulltext",
            )
            for raw_result in self.search_index.search(query_string)
        ]
