import pytest
from typing import List
from src.data import InputDocument
from src.search import SearchResult, SearchResultMeta
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
from src.search_hybrid import combine_results
from tests.conftest import FixtureResultSets
from pprint import pprint


def test_fulltext_search(input_documents: List[InputDocument]):
    fts_engine = FullTextSearchEngine()
    fts_engine.index(input_documents)

    results = fts_engine.search("play")

    assert results[0].name == "Play Art"
    assert results[0].search_meta.score == 33.607
    assert results[0].search_meta.type == "fulltext"
    assert results[0].application_ref == "1:0x123:8"
    assert (
        results[0].project_id
        == "0xf944d9fca398a4cb7f4d9b237049ad807d20f9151c254a6ad098672c13bce124"
    )
    assert results[0].round_id == "0x123"
    assert results[0].round_application_id == "8"
    assert results[0].chain_id == 1


@pytest.mark.skip(
    reason="disabled by default as loading the language model takes a relatively long time"
)
def test_semantic_search(input_documents: List[InputDocument]):
    ss_engine = SemanticSearchEngine()
    ss_engine.index(input_documents)

    results = ss_engine.search("open source")

    assert len(results) == 10
    assert results[0].application_ref == "1:0x123:152"
    assert (
        results[0].project_id
        == "0xbbe67a3d581624ace15b9c0e593fe548dc9f2df0d838df85a4a569d24601cadc"
    )
    assert results[0].round_id == "0x123"
    assert results[0].round_application_id == "152"
    assert results[0].chain_id == 1
    assert results[0].name == "Open Source AI Podcast"
    assert results[0].search_meta.score == 0.5276312828063965
    assert results[0].search_meta.type == "semantic"


def test_hybrid_search_with_strongly_relevant_keywords(result_sets: FixtureResultSets):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
    )
    assert results[0].name == "The Follow Black Hare"
    assert len(results) == 1


def test_hybrid_search_with_typo(result_sets: FixtureResultSets):
    results = combine_results(
        semantic_results=result_sets.semantic_blck_hare,
        fulltext_results=result_sets.fulltext_blck_hare,
    )
    assert len(results) == 2
    assert results[0].name == "The Follow Black Hare"
    assert results[1].name == "Sungura Mjanja Refi"


def test_hybrid_search_with_custom_fulltext_std_dev_factor(
    result_sets: FixtureResultSets,
):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
        fulltext_std_dev_factor=1,
    )
    assert len(results) == 2
    assert results[0].name == "The Follow Black Hare"
    assert results[1].name == "Blacks on Blockchain"


def test_hybrid_search_with_custom_semantic_score_cutoff(
    result_sets: FixtureResultSets,
):
    pass


def test_search_result_computed_properties():
    result = SearchResult(
        application_ref="1:0x123:0",
        round_id="0x123",
        round_application_id="0",
        chain_id=10,
        project_id="0x1",
        name="Example",
        description_markdown="# Header\n\nText",
        website_url="https://example.com",
        banner_image_cid="abc123",
        search_meta=SearchResultMeta(score=1.5, type="fulltext"),
    )

    assert result.banner_image_url == "https://ipfs.io/ipfs/abc123"
    assert result.description_html == "<h1>Header</h1>\n<p>Text</p>"
    assert result.description_plain == "Header\nText"
