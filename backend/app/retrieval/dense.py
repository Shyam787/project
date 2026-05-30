from typing import Protocol

from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.models import AuthorizedRetrievalScope, RetrievalCandidate
from app.retrieval.qdrant import qdrant_document_filter, tenant_collection_name


class VectorSearchClient(Protocol):
    async def search(
        self,
        *,
        collection_name: str,
        query_vector: list[float],
        query_filter: dict,
        limit: int,
    ) -> list[dict]:
        """Run a tenant-scoped vector search."""


class DenseRetriever:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_client: VectorSearchClient,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_client = vector_client

    async def search(
        self,
        *,
        query: str,
        scope: AuthorizedRetrievalScope,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        query_vector = await self._embedding_provider.embed_query(query)
        raw_results = await self._vector_client.search(
            collection_name=tenant_collection_name(scope.tenant_id),
            query_vector=query_vector,
            query_filter=qdrant_document_filter(scope),
            limit=top_k,
        )
        candidates: list[RetrievalCandidate] = []
        for result in raw_results:
            payload = result.get("payload", {})
            document_id = payload.get("document_id", "")
            tenant_id = payload.get("tenant_id", "")
            if not scope.allows(tenant_id=tenant_id, document_id=document_id):
                continue
            candidates.append(
                RetrievalCandidate(
                    chunk_id=str(result["id"]),
                    document_id=document_id,
                    tenant_id=tenant_id,
                    text=payload.get("chunk_text", ""),
                    retrieval_source="dense",
                    retrieval_score=float(result.get("score", 0.0)),
                    rank=len(candidates) + 1,
                    metadata=payload.get("metadata", {}),
                )
            )
        return candidates
