import pytest
import pathlib
import json
from src.data import load_projects_json, load_applications_dir
from pprint import pprint


def test_load_valid_document(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "id": "0x0000000000000000000000000000000000000000000000000000000000000001",
                    "metadata": {
                        "title": "Foo",
                        "description": "A foo project",
                        "website": "https://example.com/foo",
                        "bannerImg": "00000000000000000000000000000000000000000000000000000000foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 1


def test_ignore_document_without_project_id(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "metadata": {
                        "title": "Foo",
                        "description": "A foo project",
                        "website": "https://example.com/foo",
                        "bannerImg": "00000000000000000000000000000000000000000000000000000000foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 0


def test_ignore_document_without_title(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "id": "0x0000000000000000000000000000000000000000000000000000000000000001",
                    "metadata": {
                        "description": "A foo project",
                        "website": "https://example.com/foo",
                        "bannerImg": "00000000000000000000000000000000000000000000000000000000foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 0


@pytest.mark.skip(reason="we probably don't want this")
def test_ignore_document_without_description(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "id": "0x0000000000000000000000000000000000000000000000000000000000000001",
                    "metadata": {
                        "title": "Foo",
                        "website": "https://example.com/foo",
                        "bannerImg": "00000000000000000000000000000000000000000000000000000000foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 0


def test_ignore_document_without_website(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "id": "0x0000000000000000000000000000000000000000000000000000000000000001",
                    "metadata": {
                        "title": "Foo",
                        "description": "A foo project",
                        "bannerImg": "00000000000000000000000000000000000000000000000000000000foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 0


def test_accept_document_without_banner(tmp_path: pathlib.Path):
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "id": "0x0000000000000000000000000000000000000000000000000000000000000001",
                    "metadata": {
                        "title": "Foo",
                        "description": "A foo project",
                        "website": "https://example.com/foo",
                    },
                }
            ]
        )
    )

    documents = load_projects_json(str(projects_json))
    assert len(documents) == 1


def test_load_applications_dir():
    input_documents = load_applications_dir(
        "tests/fixtures/sample_applications_by_round"
    )
    assert len(input_documents) == 62

    input_documents = load_applications_dir(
        "tests/fixtures/sample_applications_by_round", filter_duplicate_projects=False
    )
    assert len(input_documents) == 64
