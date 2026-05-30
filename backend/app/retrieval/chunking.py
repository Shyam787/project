from collections.abc import Iterable
from uuid import uuid4

from app.retrieval.models import ChunkRecord

TARGET_CHUNK_TOKENS = 600
MIN_CHUNK_TOKENS = 400
MAX_CHUNK_TOKENS = 700
OVERLAP_TOKENS = 80


def tokenize(text: str) -> list[str]:
    return [token for token in text.split() if token.strip()]


def build_chunks(
    *,
    tenant_id: str,
    document_id: str,
    text: str,
    source_page: int | None = None,
    metadata: dict | None = None,
    target_tokens: int = TARGET_CHUNK_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[ChunkRecord]:
    tokens = tokenize(text)
    if not tokens:
        return []

    safe_target = min(max(target_tokens, MIN_CHUNK_TOKENS), MAX_CHUNK_TOKENS)
    if len(tokens) <= safe_target:
        return [
            ChunkRecord(
                chunk_id=str(uuid4()),
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_text=text.strip(),
                chunk_index=0,
                source_page=source_page,
                metadata=metadata or {},
            )
        ]

    safe_overlap = min(overlap_tokens, safe_target // 2)
    step = safe_target - safe_overlap
    chunks: list[ChunkRecord] = []

    for chunk_index, start in enumerate(range(0, len(tokens), step)):
        chunk_tokens = tokens[start : start + safe_target]
        if not chunk_tokens:
            break
        chunks.append(
            ChunkRecord(
                chunk_id=str(uuid4()),
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_text=" ".join(chunk_tokens),
                chunk_index=chunk_index,
                source_page=source_page,
                metadata=metadata or {},
            )
        )
        if start + safe_target >= len(tokens):
            break
    return chunks


def chunk_many(records: Iterable[tuple[str, str, str]]) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for tenant_id, document_id, text in records:
        chunks.extend(
            build_chunks(tenant_id=tenant_id, document_id=document_id, text=text)
        )
    return chunks
