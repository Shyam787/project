import httpx

from app.retrieval.hash_embeddings import EMBEDDING_DIMENSIONS, hash_embedding
from app.retrieval.models import AuthorizedRetrievalScope, ChunkRecord, RetrievalCandidate
from app.retrieval.qdrant import qdrant_document_filter, tenant_collection_name


class QdrantVectorStore:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def ensure_collection(self, tenant_id: str) -> None:
        collection = tenant_collection_name(tenant_id)
        async with httpx.AsyncClient(timeout=10.0) as client:
            exists = await client.get(f"{self._base_url}/collections/{collection}")
            if exists.status_code == 200:
                return
            response = await client.put(
                f"{self._base_url}/collections/{collection}",
                json={
                    "vectors": {
                        "size": EMBEDDING_DIMENSIONS,
                        "distance": "Cosine",
                    }
                },
            )
            response.raise_for_status()

    async def upsert_chunks(self, *, tenant_id: str, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        await self.ensure_collection(tenant_id)
        points = [
            {
                "id": chunk.chunk_id,
                "vector": hash_embedding(chunk.chunk_text),
                "payload": {
                    "tenant_id": chunk.tenant_id,
                    "document_id": chunk.document_id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                },
            }
            for chunk in chunks
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._base_url}/collections/{tenant_collection_name(scope.tenant_id)}/points/search",
                json={
                    "vector": hash_embedding(query),
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
