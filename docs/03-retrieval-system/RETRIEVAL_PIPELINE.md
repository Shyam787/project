# RETRIEVAL PIPELINE

## Purpose

This document defines the authoritative retrieval pipeline for the platform.

It governs:
- retrieval execution order
- retrieval orchestration
- retrieval security
- retrieval scoring
- retrieval observability
- retrieval grounding

All retrieval implementation must comply with this pipeline.

---

# Retrieval Philosophy

The retrieval system is the core intelligence layer of the platform.

The objective is not merely:
- vector similarity search
- keyword matching

The objective is:
- secure enterprise retrieval
- grounded generation
- explainable search
- hallucination reduction
- tenant-safe retrieval

---

# Retrieval Goals

The retrieval pipeline must provide:
- semantic relevance
- lexical relevance
- RBAC-safe retrieval
- tenant isolation
- grounded context assembly
- explainable ranking
- observable retrieval behavior

---

# Retrieval Architecture Overview

The retrieval pipeline consists of:

1. Query Validation
2. Authentication
3. Tenant Resolution
4. RBAC Filtering
5. Dense Retrieval
6. Sparse Retrieval
7. Hybrid Fusion
8. Reranking
9. Top-k Selection
10. Prompt Context Assembly
11. Citation Mapping
12. Hallucination Traceability

---

# Critical Retrieval Rule

Unauthorized chunks must never:
- enter reranking
- enter prompts
- influence generation
- appear in citations

RBAC filtering occurs before generation.

---

# Retrieval Workflow

---

# Phase 1 — Query Intake

## Responsibilities

The system receives:
- user query
- user identity
- tenant identity
- conversation metadata

---

## Validation Rules

The query layer validates:
- authentication
- tenant membership
- request structure
- query size limits

Invalid requests are rejected immediately.

---

# Phase 2 — Authentication & Tenant Resolution

## Responsibilities

The system establishes:
- authenticated identity
- RBAC context
- tenant execution context

---

## Constraints

Every retrieval operation must remain:
- tenant-scoped
- RBAC-scoped

Cross-tenant retrieval is prohibited.

---

# Phase 3 — Retrieval Preparation

## Responsibilities

The system prepares:
- normalized query
- embedding generation request
- sparse retrieval query

---

## Query Normalization

Normalization may include:
- whitespace cleanup
- lowercase normalization
- stopword handling
- token cleanup

Normalization must remain deterministic.

---

# Phase 4 — Dense Retrieval

## Technology

Qdrant vector search

---

## Responsibilities

Dense retrieval provides:
- semantic similarity matching
- embedding-based ranking
- multilingual semantic search

---

## Workflow

1. query embedding generation
2. tenant-scoped vector search
3. similarity scoring
4. candidate retrieval

---

## Constraints

Dense retrieval must:
- remain namespace-scoped
- expose retrieval scores
- preserve chunk identifiers

---

# Phase 5 — Sparse Retrieval

## Technology

BM25

---

## Responsibilities

Sparse retrieval provides:
- lexical matching
- keyword relevance
- exact phrase recall

---

## Workflow

1. query tokenization
2. BM25 scoring
3. keyword candidate retrieval

---

## Constraints

Sparse retrieval must:
- remain tenant-scoped
- preserve metadata traceability

---

# Phase 6 — Hybrid Fusion

## Objective

Combine:
- semantic retrieval
- lexical retrieval

into a unified ranking system.

---

# Fusion Strategy

## Selected Algorithm

Reciprocal Rank Fusion (RRF)

---

## Why RRF

RRF improves:
- ranking stability
- semantic-keyword balance
- enterprise search relevance

RRF avoids:
- unstable score normalization
- provider-specific score dependence

---

# Fusion Workflow

1. dense ranking generation
2. sparse ranking generation
3. reciprocal rank computation
4. combined score calculation
5. merged candidate ranking

---

# Constraints

Fusion must remain:
- deterministic
- explainable
- observable

---

# Phase 7 — RBAC Enforcement

## Objective

Remove unauthorized chunks before generation.

---

# Workflow

1. document ownership validation
2. role validation
3. permission validation
4. unauthorized chunk removal

---

# Critical Constraints

Unauthorized chunks must never:
- reach reranking
- reach prompt assembly
- influence hallucination scoring

---

# Phase 8 — Reranking

## Technology

Cross-encoder reranker

---

## Responsibilities

Reranking improves:
- semantic precision
- contextual relevance
- retrieval ordering

---

# Workflow

1. authorized chunk selection
2. query-chunk pair scoring
3. semantic reranking
4. top-k refinement

---

# Constraints

Reranking only operates on:
- authorized chunks
- tenant-valid chunks

---

# Phase 9 — Top-K Selection

## Responsibilities

The pipeline selects:
- highest-confidence chunks
- grounded retrieval context
- citation-compatible chunks

---

## Constraints

Top-k selection must:
- preserve traceability
- preserve metadata
- preserve document identifiers

---

# Phase 10 — Prompt Context Assembly

## Responsibilities

The system assembles:
- grounded context
- chunk references
- citation metadata
- hallucination traceability metadata

---

## Constraints

Prompt assembly must:
- remain deterministic
- preserve chunk lineage
- preserve document lineage

---

# Retrieval Metadata

Every retrieved chunk must preserve:
- chunk_id
- document_id
- tenant_id
- retrieval score
- rerank score
- source metadata

---

# Retrieval Explainability

The platform must expose:
- retrieval scores
- reranking scores
- retrieval source visibility
- citation traceability

Opaque ranking behavior is prohibited.

---

# Retrieval Observability

The retrieval pipeline must expose:
- retrieval latency
- reranking latency
- cache hit rates
- retrieval failures
- fusion metrics

---

# Retrieval Metrics

Tracked metrics include:
- MRR
- NDCG
- precision@k
- recall@k
- hallucination correlation

---

# Retrieval Caching

## Responsibilities

The cache layer reduces:
- repeated retrieval latency
- repeated reranking overhead

---

## Constraints

Caches must remain:
- tenant-aware
- RBAC-aware
- expiration-controlled

Unsafe shared caching is prohibited.

---

# Failure Handling

Retrieval failures must:
- expose structured errors
- preserve observability
- preserve auditability

Silent retrieval failures are prohibited.

---

# Background Reindexing

The retrieval system supports:
- nightly BM25 rebuilds
- embedding refresh workflows
- retrieval quality recalibration

---

# Scalability Strategy

The retrieval pipeline supports:
- distributed Qdrant scaling
- batched embedding generation
- future GPU migration
- retrieval service extraction

---

# Governance Principle

Retrieval correctness is treated as:
- a security concern
- a grounding concern
- an explainability concern

Retrieval shortcuts are prohibited.

---

# Repository Alignment

All retrieval implementation must remain aligned with:
- SYSTEM_ARCHITECTURE.md
- MODULE_BOUNDARIES.md
- RETRIEVAL_INVARIANTS.md
- RBAC_MODEL.md
- IMPLEMENTATION_VALIDATION.md

Retrieval behavior is governed by repository intelligence.