import pytest
from typing import List
from src.data import InputProjectDocument
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


def test_fulltext_search(project_docs: List[InputProjectDocument]):
    fts_engine = FullTextSearchEngine()
    fts_engine.index_projects(project_docs)

    results = fts_engine.search("talent")

    assert results[0].document.metadata["name"] == "Talent DAO"
    assert (
        results[0].document.metadata["project_id"]
        == "0xf322b3e0289c0311be5e94db88021b82286fef6b18b4ae865632ebe401a2860d"
    )


@pytest.mark.skip(
    reason="disabled by default as loading the language model takes a relatively long time"
)
def test_semantic_search(project_docs: List[InputProjectDocument]):
    ss_engine = SemanticSearchEngine()
    ss_engine.index_projects(project_docs)

    results = ss_engine.search("open source")

    assert len(results) == 4
    assert results[0].document.metadata["name"] == "CryptoStats"
    assert results[1].document.metadata["name"] == "SimpleMap"
