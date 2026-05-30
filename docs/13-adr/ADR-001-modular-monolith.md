# ADR-001: MODULAR MONOLITH ARCHITECTURE

## Status
Accepted

---

## Context

The Enterprise RAG system requires a backend architecture that supports:

- multi-tenant isolation
- complex retrieval pipelines (BM25 + vector + reranking)
- RBAC enforcement
- hallucination scoring
- observability instrumentation
- document ingestion pipelines

A key architectural decision is required:

> Should the system be built as microservices or a modular monolith?

---

## Decision

We choose a:

> Modular Monolith Architecture (initial phase)

with clearly separated internal modules.

---

## Reasoning

### 1. Complexity Control

Microservices introduce:
- distributed debugging complexity
- network latency overhead
- deployment fragmentation

For an intern-scale production system, this increases failure risk.

---

### 2. Faster Development Velocity

A modular monolith allows:
- single deployment unit
- simpler debugging
- faster iteration cycles
- easier local development (Docker Compose)

---

### 3. Strong Internal Boundaries

Even though it is a monolith, we enforce:

- strict module separation
- clear service boundaries
- dependency inversion rules

This ensures microservice-ready design.

---

### 4. Future Migration Path

The architecture is designed to allow later splitting into:

- retrieval service
- auth service
- ingestion service
- LLM orchestration service

without rewriting core logic.

---

## Architecture Structure

The system is organized into internal modules:
/auth
/retrieval
/ingestion
/llm
/rbac
/observability
/api


Each module:
- has isolated responsibilities
- communicates via internal interfaces
- does NOT directly access unrelated modules

---

## Consequences

### Positive

- simple deployment
- easier debugging
- faster development
- consistent local environment

### Negative

- scaling requires later refactor
- single failure domain risk
- requires strict discipline to avoid coupling

---

## Enforcement Rules

- No module can directly access another module’s database logic
- All communication must pass through service interfaces
- Cross-module logic must be explicitly defined

---

## Alignment With System Goals

This decision supports:

- RBAC enforcement (centralized auth module)
- hybrid retrieval pipeline (retrieval module)
- hallucination scoring (LLM module)
- observability (global instrumentation layer)

---

## Related ADRs

- ADR-002: RBAC-before-retrieval enforcement
- ADR-003: Qdrant per-tenant isolation
- ADR-004: local-first cloud-ready deployment strategy