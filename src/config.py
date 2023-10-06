from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ipfs_gateway: str
    projects_json_path: str
