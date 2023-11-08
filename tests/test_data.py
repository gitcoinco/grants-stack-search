from typing import cast
import pytest
from src.data import (
    load_input_documents_from_file,
)


@pytest.mark.skip(reason="TODO")
def test_data_ingest_and_persist():
    pass


@pytest.mark.skip(reason="TODO")
def test_data_load():
    pass


def test_load_applications_from_file():
    input_documents = load_input_documents_from_file(
        "tests/fixtures/preprocessed_aggregated_applications.json",
    )

    assert len(input_documents) == 45
    assert (
        input_documents[0].document.metadata.get("application_ref")
        == "10:0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871:1"
    )
    assert (
        input_documents[0].document.metadata.get("payout_wallet_address")
        == "0x2661c66C99f3184Bef72fd3CeD5040398c31D277"
    )
    assert (
        input_documents[0].document.metadata.get("project_id")
        == "0x29c7846924f3b461b036f260af5e881ef1cfd3481615d0cf1c46dc4944b2144e"
    )
    assert input_documents[0].document.metadata.get("chain_id") == 10
    assert (
        input_documents[0].document.metadata.get("round_id")
        == "0x10be322DE44389DeD49c0b2b73d8c3A1E3B6D871"
    )
    assert input_documents[0].document.metadata.get("round_application_id") == "1"
    assert (
        input_documents[0].document.metadata.get("name")
        == "ReFi Medellín - Join the movement towards a more sustainable and equitable future in Medellín, Colombia "
    )
    assert (
        input_documents[0].document.metadata.get("banner_image_cid")
        == "bafkreievnfqzynzmazogzq5h2mafdyzrrnswkyld2dlgmkeaixpcwhnqh4"
    )
    assert (
        input_documents[0].document.metadata.get("logo_image_cid")
        == "bafkreibz6c2xsqfjmzjkcumntfsxfyzk73tkonj4sgqk52ftrlhwv6meje"
    )
    assert (
        input_documents[0].document.metadata.get("website_url")
        == "https://linktr.ee/refimedellin"
    )
    summary_text = cast(str, input_documents[0].document.metadata.get("summary_text"))
    assert summary_text.startswith(
        "We are the movement towards a more sustainable and equitable future"
    )
    assert len(summary_text) == 303
