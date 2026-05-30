# ENGINEERING INVARIANTS

## Purpose

This document defines the global non-negotiable engineering constraints for the entire repository.

These invariants are absolute.

No subsystem, implementation, optimization, or infrastructure change may violate them.

Engineering invariants override implementation convenience.

---

# Invariant Philosophy

The platform prioritizes:
- security
- tenant isolation
- deterministic behavior
- explainability
- observability
- auditability
- operational safety

These invariants exist to preserve enterprise-grade system guarantees.

---

# Global Invariants

---

# Invariant 1 — Tenant Isolation Is Absolute

Tenant isolation is mandatory across:
- retrieval
- storage
- caching
- generation
- observability
- audit logging

Cross-tenant leakage is prohibited under all circumstances.

---

## Enforcement Requirements

All requests must:
- resolve tenant identity
- validate namespace ownership
- enforce tenant-scoped access

Every persistence layer must remain tenant-aware.

---

# Invariant 2 — RBAC Before Generation

RBAC enforcement must occur before:
- reranking
- prompt assembly
- generation
- citation rendering

Unauthorized chunks must never reach the LLM context window.

---

## Prohibited Behavior

The following are prohibited:
- post-generation filtering
- hidden authorization assumptions
- UI-only access control

RBAC is enforced at retrieval time.

---

# Invariant 3 — Retrieval Must Be Explainable

Every generated response must remain traceable.

Generated claims must:
- reference source chunks
- reference source documents
- remain auditable

Opaque responses are prohibited.

---

# Invariant 4 — Hallucination Visibility Is Mandatory

The system must expose hallucination scoring.

Users must be able to identify:
- unsupported claims
- low-confidence responses
- weak grounding situations

Hidden hallucination handling is prohibited.

---

# Invariant 5 — Auditability Is Mandatory

All critical workflows must be auditable.

Mandatory audit coverage includes:
- uploads
- retrieval requests
- RBAC denials
- generation requests
- admin actions
- feedback submissions

Auditability is architecture-level behavior.

---

# Invariant 6 — Security Overrides Convenience

Security constraints may not be bypassed for:
- performance
- latency
- implementation simplicity
- UI convenience

Security is prioritized over optimization shortcuts.

---

# Invariant 7 — Infrastructure Must Remain Private by Default

Critical infrastructure components must not be publicly exposed.

Protected systems include:
- PostgreSQL
- Qdrant
- Redis
- internal services

Internal network isolation is mandatory.

---

# Invariant 8 — Provider Abstraction Is Mandatory

External providers must remain replaceable.

Hardcoded vendor lock-in is prohibited for:
- LLM providers
- storage providers
- embedding providers
- infrastructure providers

The architecture must remain portable.

---

# Invariant 9 — Observability Is Mandatory

Every major subsystem must expose:
- structured logs
- metrics
- tracing
- latency instrumentation
- failure visibility

Opaque execution paths are prohibited.

---

# Invariant 10 — Deterministic Workflows Only

Critical workflows must remain deterministic and explicit.

Hidden orchestration logic is prohibited.

Examples:
- retrieval ordering
- RBAC enforcement
- prompt assembly
- hallucination scoring

---

# Invariant 11 — Validation Is Required

Implementation completion requires:
- testing
- invariant validation
- observability validation
- RBAC validation
- integration validation

Compilation success alone is insufficient.

---

# Invariant 12 — Architecture Governance Is Mandatory

Major architecture changes require:
- ADR review
- dependency analysis
- invariant validation

Architecture drift is prohibited.

---

# Invariant 13 — Local-First Development Must Remain Supported

The repository must support:
- local execution
- Docker-based development
- CPU-based inference
- minimal operational cost

Development must remain accessible without paid infrastructure.

---

# Invariant 14 — Production Portability Must Be Preserved

Local development shortcuts must not:
- block Kubernetes deployment
- block Terraform deployment
- block provider replacement
- block cloud portability

The system must remain production-upgradable.

---

# Invariant 15 — Retrieval Quality Is a Core System Concern

The platform must support:
- hybrid retrieval
- reranking
- retrieval evaluation
- feedback-driven improvement

The system must not degrade into simple vector similarity search.

---

# Invariant 16 — Frontend Stability Matters

Frontend systems must:
- remain responsive
- support streaming stability
- expose citations clearly
- expose hallucination indicators clearly

Broken UI behavior is unacceptable.

---

# Invariant 17 — Sensitive Data Requires Explicit Handling

PII-sensitive metadata requires:
- controlled access
- auditability
- tenant-scoped protection
- DPDP-aware handling

Sensitive metadata must never be implicitly exposed.

---

# Invariant 18 — Repository Intelligence Is Authoritative

Repository documentation governs implementation behavior.

Implementation may not redefine:
- architecture
- ownership
- invariants
- workflows

The repository is architecture-driven.

---

# Enforcement Principle

These invariants apply to:
- backend systems
- frontend systems
- infrastructure
- observability
- AI-assisted workflows
- deployment workflows

No implementation layer is exempt.

---

# Violation Handling

Invariant violations are treated as:
- architecture failures
- security failures
- repository governance failures

Violations must be resolved before implementation acceptance.

---

# Repository Stability Principle

The repository prioritizes:
- long-term maintainability
- operational correctness
- security guarantees
- engineering discipline

All implementation must remain aligned with these invariants.