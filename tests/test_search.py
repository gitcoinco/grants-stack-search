import pytest
from typing import Dict, List
from src.util import InputDocument
from src.search import ApplicationSummary, SearchEngineResult, SearchType
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
from src.search_hybrid import combine_results
from tests.conftest import SearchResultsFixture
from pprint import pprint


def test_fulltext_search(
    input_documents: List[InputDocument],
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    fts_engine = FullTextSearchEngine()
    fts_engine.index(input_documents[:100])

    results = fts_engine.search("play")

    assert results[0].ref == "1:0x123:8"
    assert results[0].score == 34.475
    assert results[0].type == "fulltext"
    assert application_summaries_by_ref[results[0].ref].name == "Play Art"


def test_persist_and_restore_fulltext_search_index(
    input_documents: List[InputDocument],
    application_summaries_by_ref: Dict[str, ApplicationSummary],
    tmp_path,
):
    fts_engine = FullTextSearchEngine()
    fts_engine.index(input_documents[:100])
    fts_engine.save_index(tmp_path / "fts_index.json")

    fts_engine_with_loaded_index = FullTextSearchEngine()
    fts_engine_with_loaded_index.load_index(tmp_path / "fts_index.json")

    results = fts_engine_with_loaded_index.search("play")

    assert results[0].ref == "1:0x123:8"
    assert results[0].score == 34.475
    assert results[0].type == "fulltext"
    assert application_summaries_by_ref[results[0].ref].name == "Play Art"


# TODO replace with search_engines.semantic fixture
@pytest.mark.skip(
    reason="disabled by default as loading the language model takes a relatively long time"
)
def test_semantic_search(
    input_documents: List[InputDocument],
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    ss_engine = SemanticSearchEngine()
    ss_engine.index(input_documents)

    results = ss_engine.search("open source")

    assert len(results) == 100
    assert results[0].ref == "1:0x123:152"
    assert results[0].score == 0.5276312828063965
    assert results[0].type == "semantic"

    assert application_summaries_by_ref[results[0].ref].name == "Open Source AI Podcast"

    results = ss_engine.search("open source", min_score=0.6)

    assert len(results) == 0


def test_hybrid_search_with_strongly_relevant_keywords(
    result_sets: SearchResultsFixture,
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
    )

    assert application_summaries_by_ref[results[0].ref].name == "The Follow Black Hare"
    assert len(results) == 1


def test_hybrid_search_with_typo(
    result_sets: SearchResultsFixture,
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    results = combine_results(
        semantic_results=result_sets.semantic_blck_hare,
        fulltext_results=result_sets.fulltext_blck_hare,
    )
    assert len(results) == 2
    assert application_summaries_by_ref[results[0].ref].name == "The Follow Black Hare"
    assert application_summaries_by_ref[results[1].ref].name == "Sungura Mjanja Refi"


def test_hybrid_search_with_custom_fulltext_std_dev_factor(
    result_sets: SearchResultsFixture,
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
        fulltext_std_dev_factor=1,
    )
    assert len(results) == 2
    assert application_summaries_by_ref[results[0].ref].name == "The Follow Black Hare"
    assert application_summaries_by_ref[results[1].ref].name == "Blacks on Blockchain"


# @pytest.mark.only
def test_hybrid_search_excludes_semantic_results_that_were_already_in_fulltext_results():
    results = combine_results(
        fulltext_results=[
            SearchEngineResult(ref="0x1", score=0.5, type=SearchType.fulltext),
            SearchEngineResult(ref="0x999", score=0.4, type=SearchType.fulltext),
            SearchEngineResult(ref="0x123", score=0.1, type=SearchType.fulltext),
        ],
        semantic_results=[
            SearchEngineResult(ref="0x2", score=0.4, type=SearchType.semantic),
            SearchEngineResult(ref="0x999", score=0.2, type=SearchType.semantic),
        ],
        fulltext_std_dev_factor=1,
    )

    assert len(results) == 3
    assert results[0].ref == "0x1"
    assert results[1].ref == "0x999"
    assert results[2].ref == "0x2"


def test_hybrid_search_with_custom_semantic_score_cutoff():
    pass
