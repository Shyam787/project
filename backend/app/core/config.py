from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "enterprise-rag"
    app_env: str = "local"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    enable_docs: bool = True

    postgres_db: str = "enterprise_rag"
    postgres_user: str = "enterprise_rag"
    postgres_password: str = Field(default="", repr=False)
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    keycloak_realm: str = "enterprise-rag"
    keycloak_issuer_url: str = "http://keycloak:8080/realms/enterprise-rag"
    keycloak_audience: str = "enterprise-rag-api"
    keycloak_jwks_url: str = (
        "http://keycloak:8080/realms/enterprise-rag/protocol/openid-connect/certs"
    )
    auth_jwks_json: str = Field(default="", repr=False)
    auth_algorithm: Literal["RS256"] = "RS256"

    groq_api_key: str = Field(default="", repr=False)
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.1-8b-instant"
    local_auto_migrate: bool = True
    storage_root: str = "storage/uploads"

    @computed_field
    @property
    def database_url(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            "postgresql+asyncpg://"
            f"{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @computed_field
    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
