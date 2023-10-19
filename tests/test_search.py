import pytest
from typing import List
from src.data import InputProjectDocument
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine


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

    # TODO test these computed properties separately
    assert (
        results[0].description_plain
        == "Play Art is a decentralized ART and NFT creation platform, for creating artistic NFT that have a weirdly unique prop called live drawing."
    )
    assert (
        results[0].banner_image_cid
        == "bafkreidb27k2tuudsp3xfkiiksthwhq7bqqpx5rm6vsnmeo7mkrzt5zdcy"
    )
    assert (
        results[0].banner_image_url
        == "https://ipfs.io/ipfs/bafkreidb27k2tuudsp3xfkiiksthwhq7bqqpx5rm6vsnmeo7mkrzt5zdcy"
    )


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
