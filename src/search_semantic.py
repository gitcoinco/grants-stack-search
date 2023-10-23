import time
import logging
from langchain.vectorstores import Chroma
from typing import List
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from src.data import InputProjectDocument
from src.search import SearchEngine, SearchResult

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


class SemanticSearchEngine(SearchEngine):
    db: Chroma

    def load(self, persist_directory: str) -> None:
        logging.debug(
            "attempting to load persisted chromadb from %s", persist_directory
        )

        persisted_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_function,
        )

        sample = persisted_db.get(limit=1)
        if len(sample["ids"]) == 0:
            logging.debug(
                "could not load persisted chromadb from %s", persist_directory
            )
            raise Exception("No persisted data")
        else:
            logging.debug("chromadb loaded from %s", persist_directory)
            self.db = persisted_db

    def index_projects(
        self, project_docs: List[InputProjectDocument], persist_directory: str
    ) -> None:
        start_time = time.perf_counter()

        raw_documents = [project_document.document for project_document in project_docs]

        self.db = Chroma.from_documents(
            documents=raw_documents,
            embedding=embedding_function,
            ids=[doc.metadata["project_id"] for doc in raw_documents],
            persist_directory=persist_directory,
        )

        logging.debug(
            "indexed %d projects in %.2f seconds with chroma",
            len(project_docs),
            time.perf_counter() - start_time,
        )

        self.db.persist()

    def search(self, query_string: str) -> List[SearchResult]:
        return [
            SearchResult.from_input_document(
                input_document=InputProjectDocument(raw_doc),
                # TODO normalize score to 0..1
                score=score,
            )
            for raw_doc, score in self.db.similarity_search_with_relevance_scores(
                query_string, k=10
            )
        ]

    def _hack_get_db(self) -> Chroma:
        return self.db
