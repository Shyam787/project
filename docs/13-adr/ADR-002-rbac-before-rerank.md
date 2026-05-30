# ADR-002: RBAC ENFORCEMENT BEFORE RERANKING

## Status
Accepted

---

## Context

The retrieval pipeline consists of multiple stages:

1. RBAC filtering
2. Hybrid retrieval (BM25 + vector search)
3. RRF fusion
4. Cross-encoder reranking
5. Context assembly
6. LLM generation

A critical decision must be made:

> Should RBAC filtering happen before or after reranking?

---

## Decision

RBAC filtering MUST happen:

> BEFORE reranking and BEFORE any retrieval results are processed further than initial fetch.

---

## Reasoning

### 1. Security Containment

If RBAC is applied after reranking:
- unauthorized documents may influence ranking
- reranker sees restricted content
- leakage risk increases

---

### 2. Preventing Model Contamination

Cross-encoder reranker evaluates relevance.

If it sees unauthorized data:
- it may prioritize sensitive chunks
- system behavior becomes unpredictable

---

### 3. Observability Integrity

Metrics like:
- MRR
- NDCG
- precision@k

must reflect ONLY authorized data.

Otherwise:
- evaluation becomes invalid
- system metrics become misleading

---

### 4. Compliance Requirement

Enterprise compliance requires:

- no processing of unauthorized data at any stage
- not even transient exposure in ranking layers

---

## Final Execution Order
Auth → Tenant Resolve → RBAC Filter → Retrieval → RRF → Rerank → Context → LLM


---

## Consequences

### Positive

- strict security boundary
- clean ranking system
- compliant evaluation metrics

---

### Negative

- slightly reduced reranking candidate pool
- requires careful filtering optimization

---

## Enforcement Rule

RBAC filtering must ensure:

- unauthorized documents NEVER reach reranker
- reranker input is fully pre-filtered
- LLM context is strictly scoped

---

## Violation Definition

Any system that:
- reranks before RBAC filtering
- allows reranker visibility into restricted documents

is considered a **critical security failure**

---

## Related ADRs

- ADR-001: Modular monolith architecture
- ADR-003: Qdrant per-tenant isolation
- ADR-004: Local-first deployment strategy