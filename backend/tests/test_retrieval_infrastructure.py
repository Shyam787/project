import pytest

from app.retrieval.chunking import build_chunks
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.models import AuthorizedRetrievalScope, ChunkRecord
from app.retrieval.qdrant import qdrant_document_filter, tenant_collection_name
from app.retrieval.sparse import BM25SparseIndex


def _chunk(chunk_id: str, document_id: str, tenant_id: str, text: str) -> ChunkRecord:
    return ChunkRecord(
        chunk_id=chunk_id,
        document_id=document_id,
        tenant_id=tenant_id,
        chunk_text=text,
        chunk_index=0,
    )


def test_chunking_preserves_traceability():
    chunks = build_chunks(
        tenant_id="tenant-a",
        document_id="doc-1",
        text=" ".join(["policy"] * 900),
        source_page=3,
    )

    assert len(chunks) > 1
    assert chunks[0].tenant_id == "tenant-a"
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].source_page == 3


def test_chunking_preserves_short_document_formatting():
    text = "Passwords must contain:\n- minimum 14 characters\n- one uppercase letter"

    chunks = build_chunks(tenant_id="tenant-a", document_id="doc-1", text=text)

    assert len(chunks) == 1
    assert chunks[0].chunk_text == text


def test_qdrant_scope_uses_tenant_namespace_and_authorized_documents():
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-2", "doc-1"},
    )

    assert tenant_collection_name(scope.tenant_id) == "tenant_tenant-a"
    assert qdrant_document_filter(scope)["must"][1]["match"]["any"] == [
        "doc-1",
        "doc-2",
    ]


def test_bm25_filters_by_authorized_scope_before_returning_results():
    chunks = [
        _chunk("chunk-1", "doc-1", "tenant-a", "security policy access"),
        _chunk("chunk-2", "doc-2", "tenant-a", "security policy secret"),
        _chunk("chunk-3", "doc-3", "tenant-b", "security policy leak"),
    ]
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-1"},
    )
    index = BM25SparseIndex(tenant_id="tenant-a", chunks=chunks)

    results = index.search(query="security policy", scope=scope, top_k=10)

    assert [result.document_id for result in results] == ["doc-1"]


def test_rrf_is_deterministic_and_traceable():
    dense = [
        _chunk("chunk-1", "doc-1", "tenant-a", "alpha").model_dump(),
        _chunk("chunk-2", "doc-2", "tenant-a", "beta").model_dump(),
    ]
    dense_candidates = [
        {
            "chunk_id": item["chunk_id"],
            "document_id": item["document_id"],
            "tenant_id": item["tenant_id"],
            "text": item["chunk_text"],
            "retrieval_source": "dense",
            "retrieval_score": 0.9 - index,
            "rank": index + 1,
            "metadata": {},
        }
        for index, item in enumerate(dense)
    ]
    sparse_candidates = list(reversed(dense_candidates))

    from app.retrieval.models import RetrievalCandidate

    fused = reciprocal_rank_fusion(
        [
            [RetrievalCandidate(**candidate) for candidate in dense_candidates],
            [RetrievalCandidate(**candidate) for candidate in sparse_candidates],
        ],
        top_k=2,
    )

    assert [candidate.chunk_id for candidate in fused] == ["chunk-1", "chunk-2"]
    assert all(candidate.retrieval_source == "rrf" for candidate in fused)


@pytest.mark.anyio
async def test_dense_retriever_enforces_scope_on_client_results():
    class FakeEmbeddingProvider:
        async def embed_query(self, query: str) -> list[float]:
            return [0.1, 0.2]

        async def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.1, 0.2] for _ in texts]

    class FakeVectorClient:
        async def search(self, **kwargs) -> list[dict]:
            return [
                {
                    "id": "chunk-1",
                    "score": 0.8,
                    "payload": {
                        "tenant_id": "tenant-a",
                        "document_id": "doc-1",
                        "chunk_text": "allowed",
                    },
                },
                {
                    "id": "chunk-2",
                    "score": 0.9,
                    "payload": {
                        "tenant_id": "tenant-b",
                        "document_id": "doc-2",
                        "chunk_text": "blocked",
                    },
                },
            ]

    retriever = DenseRetriever(
        embedding_provider=FakeEmbeddingProvider(),
        vector_client=FakeVectorClient(),
    )
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-1"},
    )

    results = await retriever.search(query="policy", scope=scope, top_k=10)

    assert [result.chunk_id for result in results] == ["chunk-1"]
