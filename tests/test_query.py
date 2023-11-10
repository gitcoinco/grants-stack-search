import pytest
from src.search_query import SearchQuery


def test_default_parameters():
    q = SearchQuery("open source")
    assert q.params.strategy == "hybrid"
    assert q.params.hybrid_search_fulltext_std_dev_factor == 1
    assert q.params.semantic_score_cutoff == 0.15


def test_set_search_strategy():
    q = SearchQuery("open source --strategy=semantic")
    assert q.params.strategy == "semantic"


def test_empty_query_raises_exception():
    with pytest.raises(Exception):
        SearchQuery("    ")


def test_set_fulltext_std_dev_factor_for_hybrid_search():
    q = SearchQuery(
        "open source --strategy=hybrid --hybrid-search-fulltext-std-dev-factor=4"
    )
    assert q.params.hybrid_search_fulltext_std_dev_factor == 4


def test_set_semantic_score_cutoff_for_hybrid_search():
    q = SearchQuery("open source --strategy=hybrid --semantic-score-cutoff=0.05")
    assert q.params.semantic_score_cutoff == 0.05
