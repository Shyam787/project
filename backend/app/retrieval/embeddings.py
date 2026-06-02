import asyncio
from typing import Protocol

BGE_M3_MODEL_NAME = "BAAI/bge-m3"
BGE_M3_EMBEDDING_DIMENSIONS = 1024


class EmbeddingProvider(Protocol):
    async def embed_query(self, query: str) -> list[float]:
        """Generate a query embedding using the configured embedding provider."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate document embeddings using the configured embedding provider."""


class LocalBgeM3EmbeddingProvider:
    """CPU local BGE-M3 embedding provider using sentence-transformers."""

    model_name = BGE_M3_MODEL_NAME

    def __init__(self, model_name: str = BGE_M3_MODEL_NAME, *, batch_size: int = 64) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._load_lock = asyncio.Lock()

    async def embed_query(self, query: str) -> list[float]:
        vectors = await self.embed_documents([query])
        return vectors[0] if vectors else [0.0] * BGE_M3_EMBEDDING_DIMENSIONS

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = await self._get_model()
        vectors = await asyncio.to_thread(
            model.encode,
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        if hasattr(vectors, "tolist"):
            return vectors.tolist()
        return [list(vector) for vector in vectors]

    async def _get_model(self):
        if self._model is not None:
            return self._model
        async with self._load_lock:
            if self._model is None:
                self._model = await asyncio.to_thread(self._load_model)
        return self._model

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "BGE-M3 embeddings require sentence-transformers. "
                "Install backend dependencies before ingesting or querying documents."
            ) from exc
        return SentenceTransformer(self.model_name)


class BgeM3EmbeddingProvider:
    model_name = BGE_M3_MODEL_NAME

    def __init__(self, runtime: EmbeddingProvider | None = None) -> None:
        self._runtime = runtime or LocalBgeM3EmbeddingProvider()

    async def embed_query(self, query: str) -> list[float]:
        return await self._runtime.embed_query(query)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._runtime.embed_documents(texts)
