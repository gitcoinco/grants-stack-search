import json, typing
import logging
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from starlette.responses import Response
from urllib.parse import urljoin
from dotenv import load_dotenv
from markdown import markdown
from strip_markdown import strip_markdown
from src.config import Settings
from src.data import load_project_dataset_into_chroma_db


######################################################################
# SETUP


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()
# how to make `type: ignore` unnecessary here?
settings = Settings()  # type: ignore


######################################################################
# STATE

app = FastAPI()
db = load_project_dataset_into_chroma_db(settings.projects_json_path)


######################################################################
# UTILITIES


# Note: this is not async-friendly
class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")


class Project(BaseModel):
    id: str
    name: str
    description: str
    description_html: str
    website_url: str
    banner_image_url: str


class ProjectsSearchResponse(BaseModel):
    results: list[Project]


def document_to_project(content: str, metadata: dict) -> Project:
    return Project(
        id=metadata["project_id"],
        name=metadata["name"],
        description=strip_markdown(content),
        description_html=markdown(content, extensions=["mdx_linkify"]),
        website_url=metadata["website_url"],
        banner_image_url=urljoin(
            settings.ipfs_gateway, "ipfs/" + metadata["banner_image_cid"]
        )
        if "banner_image_cid" in metadata
        else "about:blank",
    )


######################################################################
# API ROUTES


@app.get("/search", response_class=PrettyJSONResponse)
def search(q: str) -> ProjectsSearchResponse:
    if q.strip() == "":
        return ProjectsSearchResponse(results=[])

    docs = db.similarity_search(q)
    projects = [document_to_project(d.page_content, d.metadata) for d in docs]
    return ProjectsSearchResponse(results=projects)


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> Project | None:
    result = db.get(project_id)
    if len(result["ids"]) == 0:
        return None
    else:
        return document_to_project(
            content=result["documents"][0], metadata=result["metadatas"][0]
        )


app.mount("/static", StaticFiles(directory="static"), name="static")
