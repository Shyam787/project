from typing import Protocol


class EmbeddingProvider(Protocol):
    async def embed_query(self, query: str) -> list[float]:
        """Generate a query embedding using the configured embedding provider."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate document embeddings using the configured embedding provider."""


class BgeM3EmbeddingProvider:
    model_name = "BAAI/bge-m3"

    def __init__(self, runtime: EmbeddingProvider) -> None:
        self._runtime = runtime

    async def embed_query(self, query: str) -> list[float]:
        return await self._runtime.embed_query(query)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._runtime.embed_documents(texts)
