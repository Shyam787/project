import json
from pathlib import Path

import yaml
from prometheus_client import generate_latest

from app.observability.metrics import (
    observe_hallucination_score,
    record_rbac_denial,
    record_stage_latency,
    record_tenant_violation,
    set_retrieval_quality,
)


def test_observability_metrics_are_exported():
    record_stage_latency(tenant_id="tenant-a", stage="retrieval", seconds=0.1)
    record_rbac_denial(tenant_id="tenant-a", operation="document_read")
    record_tenant_violation(tenant_id="tenant-a", operation="retrieval")
    observe_hallucination_score(tenant_id="tenant-a", score=0.2)
    set_retrieval_quality(
        tenant_id="tenant-a",
        document_set="internal",
        metric="precision_at_k",
        value=0.8,
    )

    payload = generate_latest().decode("utf-8")

    assert "enterprise_rag_stage_latency_seconds" in payload
    assert "enterprise_rag_rbac_denials_total" in payload
    assert "enterprise_rag_tenant_violation_attempts_total" in payload
    assert "enterprise_rag_hallucination_score" in payload
    assert "enterprise_rag_retrieval_quality" in payload
    assert 'document_set="internal"' in payload


def test_prometheus_and_grafana_configs_are_valid():
    root = Path(__file__).resolve().parents[2]
    prometheus = yaml.safe_load(
        (root / "observability/prometheus/prometheus.yml").read_text()
    )
    alerts = yaml.safe_load((root / "observability/prometheus/alerts.yml").read_text())
    dashboard = json.loads(
        (root / "observability/grafana/dashboards/enterprise-rag-overview.json").read_text()
    )

    assert prometheus["rule_files"] == ["/etc/prometheus/alerts.yml"]
    assert alerts["groups"][0]["rules"]
    assert dashboard["title"] == "Enterprise RAG Overview"
    assert any(
        panel["title"] == "Retrieval Quality by Document Set"
        for panel in dashboard["panels"]
    )
