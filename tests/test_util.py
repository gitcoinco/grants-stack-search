from src.util import ApplicationFileLocator


def test_application_file_locator_ensures_address_is_checksummed():
    locator = ApplicationFileLocator.from_string(
        "10:0xb5c0939a9bb0c404b028d402493b86d9998af55e"
    )
    assert locator.chain_id == 10
    assert locator.round_id == "0xB5C0939A9BB0C404b028D402493b86D9998af55e"
