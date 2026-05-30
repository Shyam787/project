from app.hallucination.scoring import (
    extract_claims,
    score_hallucination,
    validate_citations,
    verify_response,
)
from app.retrieval.context import assemble_retrieval_context
from app.retrieval.models import RetrievalCandidate


def _context():
    return assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            RetrievalCandidate(
                chunk_id="chunk-1",
                document_id="doc-1",
                tenant_id="tenant-a",
                text="The policy requires annual access review.",
                retrieval_source="rrf",
                retrieval_score=0.5,
                rerank_score=0.9,
                rank=1,
            )
        ],
    )


def test_citation_validation_rejects_unknown_citation_ids():
    valid, invalid = validate_citations(
        response_text="Annual access review is required [c1]. Unknown [c9].",
        context=_context(),
    )

    assert valid == ["c1"]
    assert invalid == ["c9"]


def test_extract_claims_keeps_numbered_lines_together():
    claims = extract_claims(
        "1. VPN access is required for remote employees [c1].\n"
        "2. Access reviews are conducted every 90 days [c1]."
    )

    assert claims == [
        "1. VPN access is required for remote employees [c1].",
        "2. Access reviews are conducted every 90 days [c1].",
    ]


def test_hallucination_scoring_marks_grounded_cited_claim_supported():
    result = score_hallucination(
        response_text="The policy requires annual access review [c1].",
        context=_context(),
    )

    assert result.score == 0
    assert result.confidence == "high"
    assert result.unsupported_claims == []


def test_hallucination_scoring_exposes_unsupported_claims():
    result = score_hallucination(
        response_text="The policy requires biometric scans every day.",
        context=_context(),
    )

    assert result.score == 1
    assert result.confidence == "low"
    assert result.unsupported_claims


def test_response_verification_penalizes_invalid_citations():
    verification = verify_response(
        response_text="The policy requires annual access review [c9].",
        context=_context(),
    )

    assert verification.invalid_citation_ids == ["c9"]
    assert verification.hallucination.score == 1
    assert verification.hallucination.confidence == "low"
