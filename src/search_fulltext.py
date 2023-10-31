import time
import logging
from lunr import lunr
from typing import List
from src.data import InputProjectDocument
from src.search import SearchEngine, SearchResult


class FullTextSearchEngine(SearchEngine):
    def index_projects(self, project_docs: List[InputProjectDocument]) -> None:
        start_time = time.perf_counter()
        self.document_index = {
            d.document.metadata["project_id"]: d for d in project_docs
        }

        self.search_index = lunr(
            ref="project_id",
            fields=[
                dict(field_name="name", boost=10),
                "description",
                "website_url",
            ],
            documents=[
                dict(
                    project_id=p.document.metadata["project_id"],
                    name=p.document.metadata["name"],
                    description=p.document.page_content,
                    website_url=p.document.metadata["website_url"],
                )
                for p in project_docs
            ],
        )
        logging.debug(
            "indexed %d projects in %.2f seconds with lunr.py",
            len(project_docs),
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
