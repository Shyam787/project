from prometheus_client import Counter, Gauge, Histogram

STAGE_LATENCY = Histogram(
    "enterprise_rag_stage_latency_seconds",
    "Latency by governed pipeline stage.",
    ["tenant_id", "stage"],
)

RBAC_DENIALS = Counter(
    "enterprise_rag_rbac_denials_total",
    "RBAC denials by tenant and operation.",
    ["tenant_id", "operation"],
)

TENANT_VIOLATIONS = Counter(
    "enterprise_rag_tenant_violation_attempts_total",
    "Tenant isolation violation attempts.",
    ["tenant_id", "operation"],
)

HALLUCINATION_SCORE = Histogram(
    "enterprise_rag_hallucination_score",
    "Hallucination score distribution.",
    ["tenant_id"],
    buckets=(0, 0.05, 0.15, 0.3, 0.5, 0.75, 1.0),
)

RETRIEVAL_QUALITY = Gauge(
    "enterprise_rag_retrieval_quality",
    "Retrieval quality metrics by tenant and document set.",
    ["tenant_id", "document_set", "metric"],
)


def record_stage_latency(*, tenant_id: str, stage: str, seconds: float) -> None:
    STAGE_LATENCY.labels(tenant_id=tenant_id, stage=stage).observe(seconds)


def record_rbac_denial(*, tenant_id: str, operation: str) -> None:
    RBAC_DENIALS.labels(tenant_id=tenant_id, operation=operation).inc()


def record_tenant_violation(*, tenant_id: str, operation: str) -> None:
    TENANT_VIOLATIONS.labels(tenant_id=tenant_id, operation=operation).inc()


def observe_hallucination_score(*, tenant_id: str, score: float) -> None:
    HALLUCINATION_SCORE.labels(tenant_id=tenant_id).observe(score)


def set_retrieval_quality(
    *,
    tenant_id: str,
    document_set: str = "all",
    metric: str,
    value: float,
) -> None:
    RETRIEVAL_QUALITY.labels(
        tenant_id=tenant_id,
        document_set=document_set,
        metric=metric,
    ).set(value)
