from typing import cast
import pytest
from src.data import (
    load_input_documents_from_applications_dir,
    load_input_documents_from_file,
)


def test_load_applications_from_file():
    input_documents = load_input_documents_from_file(
        "tests/fixtures/sample_applications_by_round/0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871.json",
        chain_id=10,
    )
    assert len(input_documents) == 35
    assert (
        input_documents[0].document.metadata.get("application_ref")
        == "10:0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871:0"
    )
    assert (
        input_documents[0].document.metadata.get("project_id")
        == "0x0737158421936b084c9d466fa2e6577101528bd53d07494e44bb4dbe34179ab5"
    )
    assert input_documents[0].document.metadata.get("chain_id") == 10
    assert (
        input_documents[0].document.metadata.get("round_id")
        == "0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871"
    )
    assert input_documents[0].document.metadata.get("round_application_id") == "0"
    assert (
        input_documents[0].document.metadata.get("name")
        == "DeSpace QF: Public Goods Funding in Space"
    )
    assert (
        input_documents[0].document.metadata.get("banner_image_cid")
        == "bafkreiggke2jjh7a6p7zn3kc6soxhwqd3azl6f3ygbpewvszuauzyfum4q"
    )
    assert (
        input_documents[0].document.metadata.get("logo_image_cid")
        == "bafkreidk4owifjkaeg5tgeswfinqx55pymlwyoc25z4d53kyz74wpqm2mm"
    )
    assert (
        input_documents[0].document.metadata.get("website_url")
        == "https://www.despace-qf.com"
    )
    summary_text = cast(str, input_documents[0].document.metadata.get("summary_text"))
    assert summary_text.startswith(
        "Project Title: DeSpace Quadratic Fund\nAbstract\nTo align the"
    )
    assert len(summary_text) == 303


def test_load_applications_dir():
    input_documents = load_input_documents_from_applications_dir(
        "tests/fixtures/sample_applications_by_round", chain_id=10
    )
    assert len(input_documents) == 64
    assert (
        input_documents[0].document.metadata.get("application_ref")
        == "10:0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871:0"
    )
    assert (
        input_documents[0].document.metadata.get("project_id")
        == "0x0737158421936b084c9d466fa2e6577101528bd53d07494e44bb4dbe34179ab5"
    )
    assert input_documents[0].document.metadata.get("chain_id") == 10
    assert (
        input_documents[0].document.metadata.get("round_id")
        == "0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871"
    )
    assert input_documents[0].document.metadata.get("round_application_id") == "0"
    assert (
        input_documents[0].document.metadata.get("name")
        == "DeSpace QF: Public Goods Funding in Space"
    )
    assert (
        input_documents[0].document.metadata.get("banner_image_cid")
        == "bafkreiggke2jjh7a6p7zn3kc6soxhwqd3azl6f3ygbpewvszuauzyfum4q"
    )
    assert (
        input_documents[0].document.metadata.get("logo_image_cid")
        == "bafkreidk4owifjkaeg5tgeswfinqx55pymlwyoc25z4d53kyz74wpqm2mm"
    )
    assert (
        input_documents[0].document.metadata.get("website_url")
        == "https://www.despace-qf.com"
    )
    summary_text = cast(str, input_documents[0].document.metadata.get("summary_text"))
    assert summary_text.startswith(
        "Project Title: DeSpace Quadratic Fund\nAbstract\nTo align the"
    )
    assert len(summary_text) == 303
