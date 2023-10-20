from typing import List
from src.search import SearchResult
import numpy as np


def combine_results(
    semantic_results: List[SearchResult], fulltext_results: List[SearchResult]
) -> List[SearchResult]:
    if len(fulltext_results) > 2:
        fulltext_subset = get_upper_outliers(fulltext_results, std_factor=3)
    else:
        fulltext_subset = fulltext_results

    semantic_subset = filter_out_low_semantic_score(semantic_results, cutoff=0.15)

    return fulltext_subset + semantic_subset


# pick items that are greater than `std_factor` standard deviations from the mean
def get_upper_outliers(results: List[SearchResult], std_factor=3) -> List[SearchResult]:
    scores = [r.score for r in results]
    cutoff = np.mean(scores) + np.std(scores) * std_factor
    return [r for r in results if r.score > cutoff]


def filter_out_low_semantic_score(
    semantic_results: List[SearchResult], cutoff=0.1
) -> List[SearchResult]:
    return [r for r in semantic_results if r.score > cutoff]
