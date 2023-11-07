import re
from langchain.schema import Document
from typing import List
from dataclasses import dataclass


class InvalidInputDocumentException(Exception):
    pass


# Wrap a Document to carry validity information together with the type
class InputDocument:
    def __init__(self, document: Document):
        if (
            isinstance(document.metadata.get("application_ref"), str)
            and isinstance(document.metadata.get("name"), str)
            and isinstance(document.metadata.get("website_url"), str)
            and isinstance(document.metadata.get("round_id"), str)
            and isinstance(document.metadata.get("chain_id"), int)
            and isinstance(document.metadata.get("round_application_id"), str)
            and isinstance(document.metadata.get("payout_wallet_address"), str)
            # banner_image_cid and logo_image_cid are optional
            and document.page_content is not None
        ):
            self.document = document
        else:
            raise InvalidInputDocumentException(
                document.metadata.get("application_ref")
            )


@dataclass
class ApplicationFileLocator:
    chain_id: int
    round_id: str


def parse_application_file_locator(
    application_file_locator_s: str,
) -> ApplicationFileLocator:
    match = re.match(r"^(\d+):(0x[0-9a-fA-F]+)$", application_file_locator_s)
    if not match:
        raise Exception(f"Invalid application locator: {application_file_locator_s}")

    return ApplicationFileLocator(chain_id=int(match.group(1)), round_id=match.group(2))


def parse_applicaton_file_locators(
    application_file_locators_s: str,
) -> List[ApplicationFileLocator]:
    return list(
        map(parse_application_file_locator, application_file_locators_s.split(","))
    )


def get_indexer_url_from_application_file_locator(
    application_file_locator: ApplicationFileLocator, indexer_base_url: str
) -> str:
    return f"{indexer_base_url}/data/{application_file_locator.chain_id}/rounds/{application_file_locator.round_id}/applications.json"
