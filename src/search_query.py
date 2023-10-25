import shlex
from typing import Union, Literal, List
from pydantic import Field, BaseModel
import argparse


class SearchParams(BaseModel):
    strategy: Union[Literal["fulltext"], Literal["semantic"], Literal["hybrid"]]
    hybrid_search_fulltext_std_dev_factor: int = Field(ge=1, le=5)
    hybrid_search_semantic_score_cutoff: float = Field(ge=0, lt=1)
    keywords: List[str]


class SearchQuery:
    def __init__(self, query_string: str):
        self.query_string = query_string

        parser = argparse.ArgumentParser()
        parser.add_argument("keywords", nargs="*")
        parser.add_argument("--strategy", default="hybrid")
        parser.add_argument("--hybrid-search-fulltext-std-dev-factor", default=3)
        parser.add_argument("--hybrid-search-semantic-score-cutoff", default=0.15)

        try:
            self.params = SearchParams(
                **vars(parser.parse_args(shlex.split(query_string)))
            )
        except SystemExit:
            raise Exception('Invalid search query: "%s"' % query_string)

    @property
    def string(self) -> str:
        return " ".join(self.params.keywords)

    @property
    def is_valid(self) -> bool:
        return len(self.params.keywords) > 0
