from typing import List
from src.search import SearchResult
import numpy as np


def combine_results(
    semantic_results: List[SearchResult],
    fulltext_results: List[SearchResult],
    fulltext_std_dev_factor=3,
    semantic_score_cutoff=0.35,
) -> List[SearchResult]:
    if len(fulltext_results) > 2:
        fulltext_subset = get_upper_outliers(
            fulltext_results, std_dev_factor=fulltext_std_dev_factor
        )
    else:
        fulltext_subset = fulltext_results

    semantic_subset = filter_out_low_semantic_score(
        semantic_results, cutoff=semantic_score_cutoff
    )

    print(len(semantic_subset))

    return fulltext_subset + semantic_subset


# pick items that are greater than `std_factor` standard deviations from the mean
def get_upper_outliers(
    results: List[SearchResult], std_dev_factor=3
) -> List[SearchResult]:
    scores = [r.search_meta.score for r in results]
    cutoff = np.mean(scores) + np.std(scores) * std_dev_factor
    return [r for r in results if r.search_meta.score > cutoff]


def filter_out_low_semantic_score(
    semantic_results: List[SearchResult], cutoff: float
) -> List[SearchResult]:
    return [r for r in semantic_results if r.search_meta.score > cutoff]
