from pydantic import BaseModel, Field


class AuthorizedRetrievalScope(BaseModel):
    tenant_id: str = Field(min_length=1)
    allowed_document_ids: set[str]

    def allows(self, *, tenant_id: str, document_id: str) -> bool:
        return tenant_id == self.tenant_id and document_id in self.allowed_document_ids


class ChunkRecord(BaseModel):
    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    chunk_text: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    source_page: int | None = None
    metadata: dict = Field(default_factory=dict)
    embedding_reference: str | None = None


class RetrievalCandidate(BaseModel):
    chunk_id: str
    document_id: str
    tenant_id: str
    text: str
    retrieval_source: str
    retrieval_score: float
    rank: int
    metadata: dict = Field(default_factory=dict)
    rerank_score: float | None = None
