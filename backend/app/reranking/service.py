import asyncio
import math
from collections.abc import Sequence
from typing import Protocol

from app.retrieval.models import AuthorizedRetrievalScope, RetrievalCandidate


class CrossEncoderProvider(Protocol):
    async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Score query/chunk pairs using the configured cross-encoder."""


class CrossEncoderReranker:
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


class LocalCrossEncoderProvider:
    """Local no-cost cross-encoder provider backed by Sentence Transformers."""

    def __init__(self, model_name: str, *, max_length: int = 512) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self._model = None
        self._load_lock = asyncio.Lock()

    async def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        model = await self._get_model()
        scores = await asyncio.to_thread(model.predict, pairs)
        return _coerce_scores(scores)

    async def _get_model(self):
        if self._model is not None:
            return self._model
        async with self._load_lock:
            if self._model is None:
                self._model = await asyncio.to_thread(self._load_model)
        return self._model

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise RuntimeError(
                "Cross-encoder reranking requires sentence-transformers. "
                "Install backend dependencies before running retrieval."
            ) from exc
        return CrossEncoder(self.model_name, max_length=self.max_length)


def _coerce_scores(scores) -> list[float]:
    if hasattr(scores, "tolist"):
        scores = scores.tolist()
    if not isinstance(scores, Sequence):
        scores = [scores]
    normalized: list[float] = []
    for score in scores:
        if isinstance(score, Sequence) and not isinstance(score, str):
            score = score[0]
        normalized.append(1.0 / (1.0 + math.exp(-float(score))))
    return normalized
