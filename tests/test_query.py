import pytest
from src.search_query import SearchQuery


def test_default_parameters():
    q = SearchQuery("open source")
    assert q.params.strategy == "fulltext"
    assert q.params.hybrid_search_std_dev_factor == 3


def test_set_search_strategy():
    q = SearchQuery("open source --strategy=semantic")
    assert q.params.strategy == "semantic"


def test_report_empty_query_as_invalid():
    q = SearchQuery("    ")
    assert q.is_valid == False


def test_set_fulltext_std_dev_factor_for_hybrid_search():
    q = SearchQuery("open source --strategy=hybrid --hybrid-search-std-dev-factor=4")
    assert q.params.hybrid_search_std_dev_factor == 4
