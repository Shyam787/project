import json
from pathlib import Path

import pytest

from app.cache.redis_cache import tenant_cache_key
from app.auth.models import IdentityContext
from app.evaluation.metrics import ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank
from app.hallucination.scoring import verify_response
from app.rbac.policies import Permission
from app.reranking.service import CrossEncoderReranker
from app.retrieval.context import assemble_retrieval_context
from app.retrieval.models import AuthorizedRetrievalScope, ChunkRecord, RetrievalCandidate
from app.retrieval.sparse import BM25SparseIndex
from app.tenant.context import resolve_tenant_context


def _dataset() -> dict:
    path = Path(__file__).with_name("evaluation_dataset.json")
    return json.loads(path.read_text())


def _identity(tenant_id: str, role: str) -> IdentityContext:
    return IdentityContext(
        user_id=f"{tenant_id}-{role}",
        tenant=resolve_tenant_context(tenant_id),
        roles={role},
        permissions={Permission.DOCUMENT_READ},
    )


def test_evaluation_dataset_is_multi_tenant_and_reproducible():
    data = _dataset()

    assert {tenant["tenant_id"] for tenant in data["tenants"]} == {"tenant-a", "tenant-b"}
    assert data["queries"][0]["expected_documents"] == ["doc-access"]


def test_rbac_and_tenant_retrieval_validation_from_dataset():
    data = _dataset()
    chunks: list[ChunkRecord] = []
    allowed_docs = set()
    for tenant in data["tenants"]:
        for index, document in enumerate(tenant["documents"]):
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{document['document_id']}-chunk",
                    document_id=document["document_id"],
                    tenant_id=tenant["tenant_id"],
                    chunk_text=document["text"],
                    chunk_index=index,
                )
            )
            if tenant["tenant_id"] == "tenant-a" and "viewer" in document["roles"]:
                allowed_docs.add(document["document_id"])

    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids=allowed_docs,
    )
    index = BM25SparseIndex(tenant_id="tenant-a", chunks=chunks)
    results = index.search(
        query="access policy review",
        scope=scope,
        top_k=10,
    )

    assert [result.document_id for result in results] == ["doc-access"]
    assert all(result.tenant_id == "tenant-a" for result in results)


@pytest.mark.anyio
async def test_rbac_before_rerank_validation_blocks_restricted_candidate():
    class Provider:
        async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
            raise AssertionError("restricted candidate reached reranker")

    reranker = CrossEncoderReranker(Provider())
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-access"},
    )

    with pytest.raises(ValueError):
        await reranker.rerank(
            query="payroll details",
            candidates=[
                RetrievalCandidate(
                    chunk_id="restricted",
                    document_id="doc-payroll",
                    tenant_id="tenant-a",
                    text="payroll export details",
                    retrieval_source="rrf",
                    retrieval_score=0.9,
                    rank=1,
                )
            ],
            scope=scope,
            top_k=1,
        )


def test_cache_validation_separates_tenant_and_rbac_context():
    tenant_a_key = tenant_cache_key(
        identity=_identity("tenant-a", "viewer"),
        category="query_response",
        parts={"query": "access policy"},
    )
    tenant_b_key = tenant_cache_key(
        identity=_identity("tenant-b", "viewer"),
        category="query_response",
        parts={"query": "access policy"},
    )
    admin_key = tenant_cache_key(
        identity=_identity("tenant-a", "tenant_admin"),
        category="query_response",
        parts={"query": "access policy"},
    )

    assert tenant_a_key != tenant_b_key
    assert tenant_a_key != admin_key


def test_retrieval_quality_metrics_are_computed():
    results = ["doc-access", "doc-payroll", "doc-access-b"]
    relevant = {"doc-access"}

    assert precision_at_k(results, relevant, 1) == 1
    assert recall_at_k(results, relevant, 1) == 1
    assert reciprocal_rank(results, relevant) == 1
    assert ndcg_at_k(results, relevant, 3) == 1


def test_hallucination_threshold_validation():
    context = assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            RetrievalCandidate(
                chunk_id="doc-access-chunk",
                document_id="doc-access",
                tenant_id="tenant-a",
                text="The access control policy requires annual access review.",
                retrieval_source="rrf",
                retrieval_score=0.8,
                rerank_score=0.9,
                rank=1,
            )
        ],
    )

    grounded = verify_response(
        response_text="The policy requires annual access review [c1].",
        context=context,
    )
    unsupported = verify_response(
        response_text="The policy requires daily biometric scans [c1].",
        context=context,
    )

    assert grounded.hallucination.score <= 0.15
    assert unsupported.hallucination.score > 0.15
