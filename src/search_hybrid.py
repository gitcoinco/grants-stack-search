from typing import List
from src.search import SearchEngineResult
import numpy as np


def combine_results(
    semantic_results: List[SearchEngineResult],
    fulltext_results: List[SearchEngineResult],
    fulltext_std_dev_factor=3,
) -> List[SearchEngineResult]:
    if len(fulltext_results) <= 2:
        fulltext_subset = fulltext_results
    else:
        fulltext_outliers = get_upper_outliers(
            fulltext_results, std_dev_factor=fulltext_std_dev_factor
        )
        if len(fulltext_outliers) > 0:
            fulltext_subset = fulltext_outliers
        else:
            fulltext_subset = fulltext_results[0:2]

    fulltext_refs = [r.ref for r in fulltext_subset]
    return fulltext_subset + [r for r in semantic_results if r.ref not in fulltext_refs]


# pick items that are greater than `std_factor` standard deviations from the mean
def get_upper_outliers(
    results: List[SearchEngineResult], std_dev_factor=3
) -> List[SearchEngineResult]:
    scores = [r.score for r in results]
    cutoff = np.mean(scores) + np.std(scores) * std_dev_factor
    return [r for r in results if r.score > cutoff]


# TODO obsolete - semantic search engine now accepts min_score
def filter_out_low_semantic_score(
    semantic_results: List[SearchEngineResult], cutoff: float
) -> List[SearchEngineResult]:
    return [r for r in semantic_results if r.score > cutoff]
