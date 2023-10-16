import time
import logging
from langchain.vectorstores import Chroma
from typing import List
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from src.data import InputProjectDocument
from src.search import SearchEngine


class SemanticSearchEngine(SearchEngine):
    db: Chroma

    def index_projects(self, project_docs: List[InputProjectDocument]) -> None:
        start_time = time.perf_counter()

        raw_documents = [project_document.document for project_document in project_docs]

        self.db = Chroma.from_documents(
            documents=raw_documents,
            embedding=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
            ids=[doc.metadata["project_id"] for doc in raw_documents],
        )

        logging.debug(
            "indexed %d projects in %.2f seconds with chroma",
            len(project_docs),
            time.perf_counter() - start_time,
        )

    def search(self, query_string: str) -> List[InputProjectDocument]:
        projects = [
            InputProjectDocument(raw_doc)
            for raw_doc in self.db.similarity_search(query_string, k=10)
        ]
        return projects

    def get_db(self) -> Chroma:
        return self.db
