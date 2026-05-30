# RETRIEVAL INVARIANTS

## Purpose

This document defines the mandatory retrieval guarantees for the entire platform.

These invariants govern:
- retrieval correctness
- hybrid retrieval behavior
- reranking behavior
- retrieval security
- grounding guarantees
- citation guarantees
- hallucination visibility

Retrieval invariants are globally binding.

---

# Retrieval Philosophy

The platform treats retrieval as:
- a security-critical workflow
- a relevance-critical workflow
- a grounding-critical workflow

The retrieval pipeline is not merely a search system.

It is the foundation for:
- answer quality
- hallucination reduction
- citation grounding
- enterprise trustworthiness

---

# Core Retrieval Principles

The retrieval architecture prioritizes:
- security before generation
- explainability
- deterministic ranking
- hybrid relevance
- observable scoring
- traceable grounding

Retrieval behavior must remain explicit and auditable.

---

# Retrieval Invariants

---

# Invariant 1 — Hybrid Retrieval Is Mandatory

The system must combine:
- dense vector retrieval
- sparse BM25 retrieval

The platform must not rely exclusively on:
- vector similarity
- keyword matching

Hybrid retrieval is required to improve enterprise search quality.

---

# Invariant 2 — Retrieval Must Remain Explainable

Every retrieved result must expose:
- retrieval source
- retrieval score
- reranking score
- originating document
- chunk identifier

Opaque ranking behavior is prohibited.

---

# Invariant 3 — RBAC Filtering Occurs Before Generation

RBAC filtering must occur before:
- reranking finalization
- prompt assembly
- LLM generation

Unauthorized chunks must never:
- enter prompts
- appear in citations
- influence generation

---

# Invariant 4 — Tenant Isolation Is Mandatory

Retrieval must remain tenant-scoped.

All retrieval operations must validate:
- tenant ownership
- namespace ownership
- document ownership

Cross-tenant retrieval leakage is prohibited.

---

# Invariant 5 — Reranking Only Uses Authorized Chunks

Cross-encoder reranking must operate only on:
- authorized chunks
- tenant-valid chunks

Unauthorized data must never influence ranking.

---

# Invariant 6 — Citation Grounding Is Mandatory

Every generated claim must remain traceable to:
- source chunks
- source documents

Generated responses without grounding are prohibited.

---

# Invariant 7 — Hallucination Visibility Is Mandatory

The platform must expose:
- hallucination scores
- unsupported claim visibility
- grounding confidence indicators

Hallucination handling must remain transparent.

---

# Invariant 8 — Retrieval Ordering Must Remain Deterministic

Retrieval ordering must follow a deterministic workflow.

Mandatory order:
1. authentication
2. tenant resolution
3. RBAC validation
4. dense retrieval
5. sparse retrieval
6. reciprocal rank fusion
7. reranking
8. top-k selection
9. prompt assembly

Implicit retrieval ordering is prohibited.

---

# Invariant 9 — Retrieval Observability Is Mandatory

The retrieval system must expose:
- retrieval latency
- reranking latency
- retrieval scores
- cache behavior
- failure visibility

Opaque retrieval execution is prohibited.

---

# Invariant 10 — Retrieval Quality Must Be Measurable

The system must track:
- MRR
- NDCG
- precision@k
- feedback trends
- hallucination trends

Retrieval quality must remain observable and improvable.

---

# Invariant 11 — Retrieval Must Remain Modular

Retrieval subsystems must remain separable:
- dense retrieval
- sparse retrieval
- fusion
- reranking
- hallucination scoring

Hidden retrieval coupling is prohibited.

---

# Invariant 12 — Retrieval Caching Must Remain Safe

Caching systems must:
- remain tenant-aware
- remain RBAC-aware
- avoid stale permission leakage

Unsafe shared caching is prohibited.

---

# Invariant 13 — Prompt Assembly Requires Traceability

Prompt assembly must preserve:
- chunk identifiers
- document identifiers
- retrieval metadata
- citation mapping

Prompt construction without traceability is prohibited.

---

# Invariant 14 — Unsupported Claims Must Remain Visible

If evidence confidence is weak:
- the system must expose hallucination risk
- unsupported responses must remain identifiable

The system must never falsely imply grounding certainty.

---

# Invariant 15 — Retrieval Must Remain Provider-Agnostic

The retrieval architecture must support replacement of:
- embedding models
- vector stores
- reranking models

Hardcoded provider coupling is prohibited.

---

# Retrieval Governance Principle

Retrieval correctness is treated as:
- a security concern
- a trust concern
- an explainability concern

Retrieval shortcuts that weaken grounding or traceability are prohibited.

---

# Violation Handling

Retrieval invariant violations are treated as:
- trust failures
- explainability failures
- architecture failures
- security failures

Violations must be resolved before implementation acceptance.

---

# Repository Alignment

All retrieval implementations must remain aligned with:
- SYSTEM_ARCHITECTURE.md
- ENGINEERING_INVARIANTS.md
- SECURITY_INVARIANTS.md
- IMPLEMENTATION_VALIDATION.md

Retrieval systems are governed by repository intelligence.