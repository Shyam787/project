import re

from app.hallucination.models import (
    ClaimGrounding,
    HallucinationResult,
    ResponseVerification,
)
from app.retrieval.context import RetrievalContext

WORD_PATTERN = re.compile(r"[A-Za-z0-9_]+")
CITATION_PATTERN = re.compile(r"\[(c\d+)\]")
MIN_SUPPORT_SCORE = 0.2
LOW_RISK_THRESHOLD = 0.25
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "is",
    "it",
    "of",
    "on",
    "policy",
    "requires",
    "the",
    "to",
    "with",
}


def extract_claims(response_text: str) -> list[str]:
    line_claims = [
        line.strip()
        for line in response_text.splitlines()
        if _is_evaluable_claim(line.strip())
    ]
    if len(line_claims) > 1 or (
        len(line_claims) == 1 and re.match(r"^\d+[\).]\s+", line_claims[0])
    ):
        return line_claims
    claims = [part.strip() for part in re.split(r"(?<=[.!?])\s+", response_text)]
    return [claim for claim in claims if claim]


def extract_citation_ids(text: str) -> list[str]:
    return CITATION_PATTERN.findall(text)


def validate_citations(
    *, response_text: str, context: RetrievalContext
) -> tuple[list[str], list[str]]:
    allowed = {citation.citation_id for citation in context.citations}
    referenced = extract_citation_ids(response_text)
    valid = sorted({citation_id for citation_id in referenced if citation_id in allowed})
    invalid = sorted({citation_id for citation_id in referenced if citation_id not in allowed})
    return valid, invalid


def score_hallucination(
    *, response_text: str, context: RetrievalContext
) -> HallucinationResult:
    if _is_safe_fallback(response_text):
        return HallucinationResult(
            score=0.0,
            confidence="high",
            unsupported_claims=[],
            claim_groundings=[],
        )
    evidence_tokens = _tokens(" ".join(chunk.text for chunk in context.chunks))
    claim_groundings: list[ClaimGrounding] = []
    unsupported: list[str] = []

    for claim in extract_claims(response_text):
        claim_text = re.sub(r"^\d+[\).]\s*", "", claim)
        claim_tokens = _tokens(CITATION_PATTERN.sub("", claim_text))
        citation_ids = extract_citation_ids(claim)
        if not claim_tokens:
            support_score = 1.0
        else:
            support_score = len(claim_tokens & evidence_tokens) / len(claim_tokens)
        supported = support_score >= MIN_SUPPORT_SCORE and bool(citation_ids)
        if not supported:
            unsupported.append(claim)
        claim_groundings.append(
            ClaimGrounding(
                claim=claim,
                supported=supported,
                support_score=round(support_score, 4),
                citation_ids=citation_ids,
            )
        )

    score = len(unsupported) / len(claim_groundings) if claim_groundings else 0.0
    return HallucinationResult(
        score=round(score, 4),
        confidence=_confidence(score),
        unsupported_claims=unsupported,
        claim_groundings=claim_groundings,
    )


def verify_response(
    *, response_text: str, context: RetrievalContext
) -> ResponseVerification:
    valid, invalid = validate_citations(response_text=response_text, context=context)
    hallucination = score_hallucination(response_text=response_text, context=context)
    if invalid:
        hallucination = hallucination.model_copy(
            update={
                "score": max(hallucination.score, 1.0),
                "confidence": "low",
            }
        )
    return ResponseVerification(
        tenant_id=context.tenant_id,
        valid_citation_ids=valid,
        invalid_citation_ids=invalid,
        hallucination=hallucination,
    )


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in (match.group(0).lower() for match in WORD_PATTERN.finditer(text))
        if token not in STOPWORDS
    }


def _confidence(score: float) -> str:
    if score <= LOW_RISK_THRESHOLD:
        return "high"
    if score <= 0.5:
        return "medium"
    return "low"


def _is_safe_fallback(response_text: str) -> bool:
    normalized = response_text.strip().lower()
    return normalized.startswith(
        (
            "i do not have enough authorized grounded evidence",
            "no authorized information was found",
        )
    )


def _is_evaluable_claim(text: str) -> bool:
    normalized = re.sub(r"^\d+[\).]\s*", "", text.strip()).strip()
    if not normalized:
        return False
    lowered = normalized.lower().rstrip(":")
    if normalized.endswith("?"):
        return False
    if lowered in {
        "based on the provided context",
        "based on the available context",
        "based on the available documents",
        "based on the provided documents",
        "answer",
        "answers",
        "possible reasons",
    }:
        return False
    if lowered.startswith(
        (
            "based on the provided context",
            "based on the available context",
            "based on the available documents",
            "based on the provided documents",
            "here are the answers",
            "i can answer the following",
        )
    ):
        return False
    return True
