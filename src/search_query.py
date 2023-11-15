import shlex
from typing import Union, Literal, List
from pydantic import Field, BaseModel
import argparse


class SearchParams(BaseModel):
    strategy: Union[Literal["fulltext"], Literal["semantic"], Literal["hybrid"]]
    hybrid_search_fulltext_std_dev_factor: int = Field(ge=1, le=5)
    semantic_score_cutoff: float = Field(ge=0, lt=1)
    keywords: List[str]


class SearchQuery:
    def __init__(
        self,
        query_string: str,
        default_hybrid_search_fulltext_std_dev_factor=1,
        default_semantic_score_cutoff=0.35,
    ):
        self.query_string = query_string

        parser = argparse.ArgumentParser()
        parser.add_argument("keywords", nargs="*")
        parser.add_argument("--strategy", default="hybrid")
        parser.add_argument(
            "--hybrid-search-fulltext-std-dev-factor",
            default=default_hybrid_search_fulltext_std_dev_factor,
        )
        parser.add_argument(
            "--semantic-score-cutoff",
            default=default_semantic_score_cutoff,
        )

        try:
            self.params = SearchParams(
                **vars(parser.parse_args(shlex.split(query_string)))
            )
        except SystemExit:
            raise Exception('Invalid search query: "%s"' % query_string)

        if len(self.params.keywords) == 0:
            raise Exception("Invalid search query: is empty")

    @property
    def string(self) -> str:
        return " ".join(self.params.keywords)

    @property
    def is_valid(self) -> bool:
        return len(self.params.keywords) > 0
