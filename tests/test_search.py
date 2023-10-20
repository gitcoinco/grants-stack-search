import pytest
from typing import List
from src.data import InputProjectDocument
from src.search import SearchResult
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
from src.search_hybrid import combine_results
from tests.conftest import ResultSets


def test_fulltext_search(project_docs: List[InputProjectDocument]):
    fts_engine = FullTextSearchEngine()
    fts_engine.index_projects(project_docs)

    results = fts_engine.search("play")

    assert results[0].name == "Play Art"
    assert (
        results[0].project_id
        == "0xf944d9fca398a4cb7f4d9b237049ad807d20f9151c254a6ad098672c13bce124"
    )
    assert results[0].score == 26.793


@pytest.mark.skip(
    reason="disabled by default as loading the language model takes a relatively long time"
)
def test_semantic_search(project_docs: List[InputProjectDocument]):
    ss_engine = SemanticSearchEngine()
    ss_engine.index_projects(project_docs)

    results = ss_engine.search("open source")

    assert len(results) == 10
    assert results[0].name == "CryptoStats"
    assert results[1].name == "Simple Map"
    assert results[0].score == 1.309523582458496


def test_hybrid_search_with_strongly_relevant_keywords(result_sets: ResultSets):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
    )
    assert len(results) == 1
    assert results[0].name == "The Follow Black Hare"


def test_hybrid_search_with_typo(result_sets: ResultSets):
    results = combine_results(
        semantic_results=result_sets.semantic_blck_hare,
        fulltext_results=result_sets.fulltext_blck_hare,
    )
    assert len(results) == 2
    assert results[0].name == "The Follow Black Hare"
    assert results[1].name == "Sungura Mjanja Refi"


def test_search_result_computed_properties():
    result = SearchResult(
        project_id="0x1",
        name="Example",
        description_markdown="# Header\n\nText",
        website_url="https://example.com",
        banner_image_cid="abc123",
        score=1.5,
    )

    assert result.banner_image_url == "https://ipfs.io/ipfs/abc123"
    assert result.description_html == "<h1>Header</h1>\n<p>Text</p>"
    assert result.description_plain == "Header\nText"
