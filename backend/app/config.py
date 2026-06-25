from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_env: str = "development"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-chat-latest"

    mp_api_key: str = ""
    semantic_scholar_api_key: str = ""

    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "BAAI/bge-m3"

    database_url: str = "sqlite:///./data/materialgpt.db"

    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    @property
    def neo4j_enabled(self) -> bool:
        return bool(self.neo4j_uri)


@lru_cache
def get_settings() -> Settings:
    return Settings()
