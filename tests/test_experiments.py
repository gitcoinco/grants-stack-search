from langchain.document_loaders import JSONLoader
from rake_nltk import Rake
import pytest
import nltk
from pprint import pprint


# NOTE: these are not real tests, we're using pytest as a testbed.


@pytest.mark.skip
def test_experiment_keyword_extraction_with_rake():
    nltk.download("stopwords")
    nltk.download("punkt")

    def get_metadata(record: dict, metadata: dict) -> dict:
        metadata["name"] = record.get("title")
        metadata["website_url"] = record.get("website")
        return metadata

    loader = JSONLoader(
        file_path=".var/1/projects.shortened.json",
        jq_schema=".[].metadata | { title, website, description }",
        content_key="description",
        metadata_func=get_metadata,
        text_content=False,
    )

    docs = loader.load()
    docs_with_title = [d.metadata["name"] + "\n\n" + d.page_content for d in docs]
    text = "\n\n".join(docs_with_title)
    r = Rake()
    r.extract_keywords_from_text(text)
    pprint(r.get_ranked_phrases_with_scores()[0:30])
