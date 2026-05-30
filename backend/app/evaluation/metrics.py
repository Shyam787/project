import math


def precision_at_k(results: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top = results[:k]
    if not top:
        return 0.0
    return len([item for item in top if item in relevant]) / len(top)


def recall_at_k(results: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top = results[:k]
    return len([item for item in top if item in relevant]) / len(relevant)


def reciprocal_rank(results: list[str], relevant: set[str]) -> float:
    for index, item in enumerate(results, start=1):
        if item in relevant:
            return 1 / index
    return 0.0


def ndcg_at_k(results: list[str], relevant: set[str], k: int) -> float:
    gains = [1 if item in relevant else 0 for item in results[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = sorted(gains, reverse=True)
    idcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(ideal))
    return dcg / idcg if idcg else 0.0
