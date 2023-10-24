import shlex
from typing import Union, Literal, List
from pydantic import Field, BaseModel
import argparse


class SearchParams(BaseModel):
    strategy: Union[Literal["fulltext"], Literal["semantic"], Literal["hybrid"]]
    hybrid_search_std_dev_factor: int = Field(ge=1, le=5)
    keywords: List[str]


class SearchQuery:
    def __init__(self, query_string: str):
        self.query_string = query_string

        parser = argparse.ArgumentParser()
        parser.add_argument("keywords", nargs="*")
        parser.add_argument("--strategy", default="fulltext")
        parser.add_argument("--hybrid-search-std-dev-factor", default=3)

        try:
            self.params = SearchParams(
                **vars(parser.parse_args(shlex.split(query_string)))
            )
        except SystemExit:
            raise Exception('error parsing search query: "%s"' % query_string)

    @property
    def string(self) -> str:
        return " ".join(self.params.keywords)

    @property
    def is_valid(self) -> bool:
        return len(self.params.keywords) > 0
