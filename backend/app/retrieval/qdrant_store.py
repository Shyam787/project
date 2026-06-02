import httpx

from app.retrieval.embeddings import BGE_M3_EMBEDDING_DIMENSIONS, EmbeddingProvider, LocalBgeM3EmbeddingProvider
from app.retrieval.models import AuthorizedRetrievalScope, ChunkRecord, RetrievalCandidate
from app.retrieval.qdrant import qdrant_document_filter, tenant_collection_name


class QdrantVectorStore:
    def __init__(self, base_url: str, embedding_provider: EmbeddingProvider | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._embedding_provider = embedding_provider or LocalBgeM3EmbeddingProvider()

    async def ensure_collection(self, tenant_id: str) -> None:
        collection = tenant_collection_name(tenant_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            exists = await client.get(f"{self._base_url}/collections/{collection}")
            if exists.status_code == 200:
                size = _collection_vector_size(exists.json())
                if size == BGE_M3_EMBEDDING_DIMENSIONS:
                    return
                await client.delete(f"{self._base_url}/collections/{collection}")
            response = await client.put(
                f"{self._base_url}/collections/{collection}",
                json={
                    "vectors": {
                        "size": BGE_M3_EMBEDDING_DIMENSIONS,
                        "distance": "Cosine",
                    }
                },
            )
            response.raise_for_status()

    async def upsert_chunks(self, *, tenant_id: str, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        await self.ensure_collection(tenant_id)
        vectors = await self._embedding_provider.embed_documents([chunk.chunk_text for chunk in chunks])
        points = [
            {
                "id": chunk.chunk_id,
                "vector": vector,
                "payload": {
                    "tenant_id": chunk.tenant_id,
                    "document_id": chunk.document_id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                },
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.put(
                f"{self._base_url}/collections/{tenant_collection_name(tenant_id)}/points",
                params={"wait": "true"},
                json={"points": points},
            )
            response.raise_for_status()

    async def search(
        self,
        *,
        query: str,
        scope: AuthorizedRetrievalScope,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        if not scope.allowed_document_ids:
            return []
        await self.ensure_collection(scope.tenant_id)
        vector = await self._embedding_provider.embed_query(query)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._base_url}/collections/{tenant_collection_name(scope.tenant_id)}/points/search",
                json={
                    "vector": vector,
                    "filter": qdrant_document_filter(scope),
                    "limit": top_k,
                    "with_payload": True,
                },
            )
            response.raise_for_status()
            raw_results = response.json().get("result", [])

        candidates: list[RetrievalCandidate] = []
        for result in raw_results:
            payload = result.get("payload", {})
            tenant_id = payload.get("tenant_id", "")
            document_id = payload.get("document_id", "")
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

    async def delete_document(self, *, tenant_id: str, document_id: str) -> None:
        await self.ensure_collection(tenant_id)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self._base_url}/collections/{tenant_collection_name(tenant_id)}/points/delete",
                params={"wait": "true"},
                json={
                    "filter": {
                        "must": [
                            {"key": "tenant_id", "match": {"value": tenant_id}},
                            {"key": "document_id", "match": {"value": document_id}},
                        ]
                    }
                },
            )
            response.raise_for_status()


def _collection_vector_size(payload: dict) -> int | None:
    vectors = (
        payload.get("result", {})
        .get("config", {})
        .get("params", {})
        .get("vectors", {})
    )
    if isinstance(vectors, dict) and "size" in vectors:
        return int(vectors["size"])
    return None
