import pytest
from typing import Dict, List
from src.util import InputDocument
from src.search import ApplicationSummary
from src.search_fulltext import FullTextSearchEngine
from src.search_semantic import SemanticSearchEngine
from src.search_hybrid import combine_results
from tests.conftest import FixtureResultSets
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

    assert len(results) == 10
    assert results[0].ref == "1:0x123:152"
    assert results[0].score == 0.5276312828063965
    assert results[0].type == "semantic"

    assert application_summaries_by_ref[results[0].ref].name == "Open Source AI Podcast"


def test_hybrid_search_with_strongly_relevant_keywords(
    result_sets: FixtureResultSets,
    application_summaries_by_ref: Dict[str, ApplicationSummary],
):
    results = combine_results(
        semantic_results=result_sets.semantic_black_hare,
        fulltext_results=result_sets.fulltext_black_hare,
    )
    assert application_summaries_by_ref[results[0].ref].name == "The Follow Black Hare"
    assert len(results) == 1


def test_hybrid_search_with_typo(
    result_sets: FixtureResultSets,
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
    result_sets: FixtureResultSets,
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


def test_hybrid_search_with_custom_semantic_score_cutoff():
    pass
