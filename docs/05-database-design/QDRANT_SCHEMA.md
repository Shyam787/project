

```md
# QDRANT_SCHEMA

## Purpose

This document defines the authoritative Qdrant schema and vector storage strategy for the platform.

It governs:
- vector organization
- tenant namespaces
- embedding metadata
- retrieval compatibility
- vector traceability

All vector storage implementation must comply with this strategy.

---

# Vector Storage Philosophy

Qdrant is responsible for:
- semantic retrieval
- embedding similarity search
- vector indexing
- tenant-scoped retrieval

Qdrant is not the authoritative source for:
- RBAC
- business logic
- audit governance

---

# Core Objectives

The vector layer must:
- remain tenant-isolated
- preserve retrieval traceability
- support hybrid retrieval
- support reranking workflows
- remain scalable

---

# Collection Strategy

Each tenant receives:
- isolated Qdrant collection or namespace

Recommended format:

```text
tenant_{tenant_id}