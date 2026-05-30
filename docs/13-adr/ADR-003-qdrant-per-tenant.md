# ADR-003: QDRANT PER-TENANT ISOLATION STRATEGY

## Status
Accepted

---

## Context

The system uses Qdrant as the vector database for embedding storage and retrieval.

Since the system is multi-tenant, we must ensure:

> Each tenant's embeddings are strictly isolated.

A design decision is required:

- single shared collection with filters
OR
- separate collections per tenant

---

## Decision

We adopt:

> Qdrant Collection Per Tenant Isolation Strategy

---

## Reasoning

### 1. Strong Isolation Guarantee

Using separate collections ensures:

- no accidental cross-tenant retrieval
- no filter misconfiguration risks
- hard boundary at storage level

---

### 2. Security Simplicity

Filter-based isolation in a shared collection introduces:
- risk of query-level mistakes
- complex RBAC filtering logic in retrieval layer

Separate collections remove this dependency.

---

### 3. Performance Predictability

Per-tenant collections:
- reduce search space
- improve retrieval latency
- simplify indexing strategy

---

### 4. Compliance Alignment

Enterprise and DPDP-aware design requires:

- strict data separation
- no shared embedding space across tenants

---

## Architecture Decision
Tenant A → Qdrant Collection: tenant_a_docs
Tenant B → Qdrant Collection: tenant_b_docs
Tenant C → Qdrant Collection: tenant_c_docs


---

## Consequences

### Positive

- strong isolation boundary
- simpler RBAC enforcement at retrieval level
- better performance per tenant
- easier debugging

---

### Negative

- more collections to manage
- increased metadata overhead
- requires collection lifecycle management

---

## Operational Rules

- Each tenant MUST have its own Qdrant collection
- Collection naming MUST follow strict convention
- No shared embeddings across tenants
- Deletion of tenant = deletion of collection

---

## Retrieval Impact

Retrieval pipeline must:

1. Resolve tenant_id
2. Route query to correct collection
3. Execute hybrid search inside that collection only

---

## Failure Modes Prevented

This decision prevents:

- cross-tenant embedding leakage
- incorrect semantic search results
- RBAC bypass via vector search

---

## Related ADRs

- ADR-001: Modular monolith architecture
- ADR-002: RBAC-before-rerank enforcement
- ADR-004: Local-first deployment strategy