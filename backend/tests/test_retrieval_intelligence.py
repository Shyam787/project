import pytest

from app.auth.models import IdentityContext
from app.rbac.policies import Permission
from app.reranking.service import CrossEncoderReranker, _coerce_scores
from app.chat.service import _grounded_extractive_answer
from app.retrieval.context import assemble_retrieval_context
from app.retrieval.models import AuthorizedRetrievalScope, RetrievalCandidate
from app.retrieval.query import normalize_query, prepare_query
from app.retrieval.sparse import normalize_tokens
from app.tenant.context import resolve_tenant_context


def _candidate(chunk_id: str, document_id: str, tenant_id: str) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        tenant_id=tenant_id,
        text=f"{chunk_id} text",
        retrieval_source="rrf",
        retrieval_score=0.5,
        rank=1,
        metadata={"source_location": {"page": 1}},
    )


def _candidate_with_text(
    chunk_id: str, document_id: str, tenant_id: str, text: str
) -> RetrievalCandidate:
    return _candidate(chunk_id, document_id, tenant_id).model_copy(
        update={"text": text, "rerank_score": 0.8}
    )


def test_query_processing_normalizes_and_builds_authorized_scope():
    identity = IdentityContext(
        user_id="user-1",
        tenant=resolve_tenant_context("tenant-a"),
        roles={"employee"},
        permissions={Permission.DOCUMENT_READ},
    )

    prepared = prepare_query(
        query="  Security   POLICY  ",
        identity=identity,
        allowed_document_ids={"doc-1"},
    )

    assert prepared.normalized_query == "security policy"
    assert prepared.scope.tenant_id == "tenant-a"
    assert prepared.scope.allowed_document_ids == {"doc-1"}


def test_empty_query_is_rejected():
    assert normalize_query(" \n\t ") == ""


def test_token_normalization_matches_plural_password_terms():
    assert "password" in normalize_tokens("What are the password requirements?")
    assert "password" in normalize_tokens("Passwords must contain special characters.")
    assert "what" not in normalize_tokens("What are the password requirements?")


def test_cross_encoder_score_logits_are_normalized_for_context_thresholds():
    scores = _coerce_scores([-2.0, 0.0, 2.0])

    assert scores[0] < scores[1] < scores[2]
    assert 0.0 < scores[0] < 1.0
    assert scores[1] == 0.5
    assert 0.0 < scores[2] < 1.0


@pytest.mark.anyio
async def test_reranker_rejects_unauthorized_candidates_before_scoring():
    class FailingProvider:
        async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
            raise AssertionError("provider must not see unauthorized candidates")

    reranker = CrossEncoderReranker(FailingProvider())
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-1"},
    )

    with pytest.raises(ValueError, match="Unauthorized candidate"):
        await reranker.rerank(
            query="policy",
            candidates=[_candidate("chunk-1", "doc-2", "tenant-a")],
            scope=scope,
            top_k=1,
        )


@pytest.mark.anyio
async def test_reranker_orders_authorized_candidates_by_cross_encoder_score():
    class Provider:
        async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
            return [0.1, 0.9]

    reranker = CrossEncoderReranker(Provider())
    scope = AuthorizedRetrievalScope(
        tenant_id="tenant-a",
        allowed_document_ids={"doc-1", "doc-2"},
    )

    results = await reranker.rerank(
        query="policy",
        candidates=[
            _candidate("chunk-1", "doc-1", "tenant-a"),
            _candidate("chunk-2", "doc-2", "tenant-a"),
        ],
        scope=scope,
        top_k=2,
    )

    assert [candidate.chunk_id for candidate in results] == ["chunk-2", "chunk-1"]
    assert results[0].rerank_score == 0.9


def test_context_assembly_preserves_citation_traceability():
    context = assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            _candidate("chunk-1", "doc-1", "tenant-a").model_copy(
                update={"rerank_score": 0.8}
            )
        ],
    )

    assert context.citations[0].citation_id == "c1"
    assert context.citations[0].chunk_id == "chunk-1"
    assert context.citations[0].document_id == "doc-1"
    assert context.citations[0].rerank_score == 0.8


def test_extractive_answer_handles_multi_question_policy_facts():
    context = assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            _candidate_with_text(
                "chunk-1",
                "doc-1",
                "tenant-a",
                "\n".join(
                    [
                        "VPN access is required for remote employees.",
                        "Access reviews are conducted every 90 days.",
                        "Document Classification: Internal",
                    ]
                ),
            )
        ],
    )

    answer = _grounded_extractive_answer(
        query=(
            "1. Who gets VPN access? "
            "2. Access reviews are conducted in how many days? "
            "3. What type of Document Classification is this?"
        ),
        context=context,
    )

    assert "VPN access is required for remote employees [c1]." in answer
    assert "Access reviews are conducted every 90 days [c1]." in answer
    assert "Document Classification: Internal [c1]." in answer


def test_extractive_answer_matches_comma_formatted_numeric_thresholds():
    context = assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            _candidate_with_text(
                "chunk-1",
                "doc-1",
                "tenant-a",
                "\n".join(
                    [
                        "Purchases above 5,000 USD require department manager approval.",
                        "Purchases above 25,000 USD require finance review and tenant administrator approval.",
                    ]
                ),
            )
        ],
    )

    answer = _grounded_extractive_answer(
        query="Who approves purchases above 25000 USD?",
        context=context,
    )

    assert "Purchases above 25,000 USD require finance review and tenant administrator approval [c1]." in answer
