from pydantic import BaseModel, Field

from app.retrieval.models import RetrievalCandidate


class Citation(BaseModel):
    citation_id: str
    chunk_id: str
    document_id: str
    tenant_id: str
    source_location: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    retrieval_score: float
    rerank_score: float | None


class RetrievalContext(BaseModel):
    tenant_id: str
    chunks: list[RetrievalCandidate]
    citations: list[Citation]


def assemble_retrieval_context(
    *,
    tenant_id: str,
    candidates: list[RetrievalCandidate],
) -> RetrievalContext:
    citations: list[Citation] = []
    for index, candidate in enumerate(candidates, start=1):
        if candidate.tenant_id != tenant_id:
            raise ValueError("Cross-tenant candidate reached context assembly.")
        citations.append(
            Citation(
                citation_id=f"c{index}",
                chunk_id=candidate.chunk_id,
                document_id=candidate.document_id,
                tenant_id=candidate.tenant_id,
                source_location=candidate.metadata.get("source_location", {}),
                metadata=candidate.metadata,
                retrieval_score=candidate.retrieval_score,
                rerank_score=candidate.rerank_score,
            )
        )
    return RetrievalContext(
        tenant_id=tenant_id,
        chunks=candidates,
        citations=citations,
    )
