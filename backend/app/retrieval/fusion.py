from collections import defaultdict

from app.retrieval.models import RetrievalCandidate

RRF_K = 60


def reciprocal_rank_fusion(
    rankings: list[list[RetrievalCandidate]],
    *,
    k: int = RRF_K,
    top_k: int,
) -> list[RetrievalCandidate]:
    scores: dict[str, float] = defaultdict(float)
    best_candidate: dict[str, RetrievalCandidate] = {}

    for ranking in rankings:
        for rank, candidate in enumerate(ranking, start=1):
            scores[candidate.chunk_id] += 1 / (k + rank)
            existing = best_candidate.get(candidate.chunk_id)
            if existing is None or candidate.retrieval_score > existing.retrieval_score:
                best_candidate[candidate.chunk_id] = candidate

    ordered_ids = sorted(
        scores,
        key=lambda chunk_id: (-scores[chunk_id], best_candidate[chunk_id].chunk_id),
    )
    fused: list[RetrievalCandidate] = []
    for rank, chunk_id in enumerate(ordered_ids[:top_k], start=1):
        candidate = best_candidate[chunk_id].model_copy(
            update={
                "retrieval_source": "rrf",
                "retrieval_score": scores[chunk_id],
                "rank": rank,
            }
        )
        fused.append(candidate)
    return fused
