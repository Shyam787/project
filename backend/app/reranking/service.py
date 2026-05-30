from typing import Protocol

from app.retrieval.models import AuthorizedRetrievalScope, RetrievalCandidate


class CrossEncoderProvider(Protocol):
    async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Score query/chunk pairs using the configured cross-encoder."""


class CrossEncoderReranker:
    model_name = "cross-encoder/ms-marco"

    def __init__(self, provider: CrossEncoderProvider) -> None:
        self._provider = provider

    async def rerank(
        self,
        *,
        query: str,
        candidates: list[RetrievalCandidate],
        scope: AuthorizedRetrievalScope,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        for candidate in candidates:
            if not scope.allows(
                tenant_id=candidate.tenant_id,
                document_id=candidate.document_id,
            ):
                raise ValueError("Unauthorized candidate reached reranking.")

        pairs = [(query, candidate.text) for candidate in candidates]
        scores = await self._provider.score_pairs(pairs)
        scored = [
            candidate.model_copy(update={"rerank_score": float(score)})
            for candidate, score in zip(candidates, scores, strict=True)
        ]
        ordered = sorted(
            scored,
            key=lambda candidate: (
                -float(candidate.rerank_score or 0.0),
                -candidate.retrieval_score,
                candidate.chunk_id,
            ),
        )
        return [
            candidate.model_copy(update={"rank": index + 1})
            for index, candidate in enumerate(ordered[:top_k])
        ]
