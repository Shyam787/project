from pydantic import BaseModel, Field


class ClaimGrounding(BaseModel):
    claim: str
    supported: bool
    support_score: float
    citation_ids: list[str] = Field(default_factory=list)


class HallucinationResult(BaseModel):
    score: float
    confidence: str
    unsupported_claims: list[str]
    claim_groundings: list[ClaimGrounding]


class ResponseVerification(BaseModel):
    tenant_id: str
    valid_citation_ids: list[str]
    invalid_citation_ids: list[str]
    hallucination: HallucinationResult
