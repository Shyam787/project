import re

from rank_bm25 import BM25Okapi

from app.retrieval.models import (
    AuthorizedRetrievalScope,
    ChunkRecord,
    RetrievalCandidate,
)

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


def normalize_tokens(text: str) -> list[str]:
    return [
        token
        for match in TOKEN_PATTERN.finditer(text)
        if (token := normalize_token(match.group(0))) and token not in STOPWORDS
    ]


def normalize_token(raw_token: str) -> str:
    token = raw_token.lower().strip("_")
    if len(token) > 4 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


class BM25SparseIndex:
    def __init__(self, *, tenant_id: str, chunks: list[ChunkRecord]) -> None:
        self._tenant_id = tenant_id
        self._chunks = [chunk for chunk in chunks if chunk.tenant_id == tenant_id]
        tokenized = [normalize_tokens(chunk.chunk_text) for chunk in self._chunks]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None

    def search(
        self,
        *,
        query: str,
        scope: AuthorizedRetrievalScope,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        if scope.tenant_id != self._tenant_id or self._bm25 is None:
            return []

        query_tokens = normalize_tokens(query)
        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)
        ranked = sorted(
            enumerate(scores),
            key=lambda item: (-float(item[1]), self._chunks[item[0]].chunk_id),
        )
        candidates: list[RetrievalCandidate] = []
        for index, score in ranked:
            chunk = self._chunks[index]
            if not scope.allows(
                tenant_id=chunk.tenant_id,
                document_id=chunk.document_id,
            ):
                continue
            candidates.append(
                RetrievalCandidate(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    tenant_id=chunk.tenant_id,
                    text=chunk.chunk_text,
                    retrieval_source="bm25",
                    retrieval_score=float(score),
                    rank=len(candidates) + 1,
                    metadata=chunk.metadata,
                )
            )
            if len(candidates) >= top_k:
                break
        return candidates
