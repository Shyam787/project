# SYSTEM WORKFLOWS

## Purpose

This document defines the authoritative end-to-end workflows for the platform.

It governs:
- ingestion workflows
- retrieval workflows
- generation workflows
- RBAC workflows
- feedback workflows
- observability workflows

All implementation must follow these workflows exactly.

---

# Workflow Philosophy

The platform prioritizes:
- deterministic execution
- explicit orchestration
- security-first ordering
- observability-first workflows
- traceable execution

Hidden workflow behavior is prohibited.

---

# Global Workflow Rules

---

# Rule 1 — Tenant Context Must Exist Everywhere

Every workflow must:
- resolve tenant identity
- validate tenant ownership
- propagate tenant context downstream

Tenant context loss is prohibited.

---

# Rule 2 — RBAC Enforcement Happens Before Generation

RBAC filtering must occur before:
- reranking
- prompt assembly
- generation

Unauthorized chunks must never enter the LLM context.

---

# Rule 3 — Every Workflow Must Be Observable

Every critical workflow must expose:
- logs
- metrics
- traces
- latency measurements

Opaque execution is prohibited.

---

# Rule 4 — Every Workflow Must Be Auditable

Critical workflows must generate audit records.

Mandatory audit coverage:
- uploads
- retrieval requests
- RBAC denials
- generation requests
- admin actions

---

# Primary System Workflows

The platform contains the following primary workflows:

1. Authentication Workflow
2. Document Upload Workflow
3. Document Ingestion Workflow
4. Query Retrieval Workflow
5. Hybrid Search Workflow
6. Reranking Workflow
7. Generation Workflow
8. Hallucination Scoring Workflow
9. Citation Grounding Workflow
10. Feedback Workflow
11. Audit Workflow
12. Reindexing Workflow

---

# Authentication Workflow

## Objective

Authenticate users and establish trusted execution context.

---

## Workflow Steps

1. user login request
2. Keycloak authentication
3. JWT issuance
4. JWT validation
5. role extraction
6. tenant resolution
7. request authorization

---

## Outputs

Produces:
- authenticated identity
- tenant context
- RBAC context

---

# Document Upload Workflow

## Objective

Accept and validate enterprise documents for ingestion.

---

## Workflow Steps

1. authenticated upload request
2. tenant validation
3. document validation
4. metadata extraction
5. permission assignment
6. upload persistence
7. ingestion job scheduling
8. audit logging

---

## Constraints

Uploads must:
- remain tenant-scoped
- remain RBAC-aware
- remain auditable

---

# Document Ingestion Workflow

## Objective

Transform uploaded documents into searchable retrieval artifacts.

---

## Workflow Steps

1. ingestion job pickup
2. document parsing
3. text extraction
4. chunk generation
5. chunk metadata creation
6. embedding generation
7. sparse index generation
8. vector persistence
9. metadata persistence
10. ingestion completion logging

---

## Outputs

Produces:
- searchable embeddings
- BM25 searchable chunks
- traceable metadata
- retrieval-ready artifacts

---

## Constraints

Ingestion must:
- preserve chunk traceability
- remain retry-safe
- remain observable
- remain tenant-aware

---

# Query Retrieval Workflow

## Objective

Retrieve authorized relevant information for generation.

---

## Workflow Steps

1. query submission
2. JWT validation
3. tenant resolution
4. RBAC validation
5. retrieval orchestration
6. retrieval scoring
7. authorized result filtering

---

## Constraints

Retrieval must:
- remain tenant-scoped
- remain RBAC-aware
- expose retrieval traceability

---

# Hybrid Search Workflow

## Objective

Combine semantic and lexical retrieval.

---

## Workflow Steps

1. dense vector retrieval
2. sparse BM25 retrieval
3. reciprocal rank fusion
4. score normalization
5. candidate aggregation

---

## Outputs

Produces:
- hybrid-ranked candidate chunks

---

## Constraints

Hybrid retrieval must:
- remain deterministic
- remain explainable
- expose retrieval scores

---

# Reranking Workflow

## Objective

Improve retrieval relevance using cross-encoder scoring.

---

## Workflow Steps

1. authorized chunk selection
2. cross-encoder scoring
3. semantic refinement
4. top-k prioritization

---

## Constraints

Reranking only operates on:
- authorized chunks
- tenant-valid chunks

Unauthorized chunks must never enter reranking.

---

# Generation Workflow

## Objective

Generate grounded enterprise responses.

---

## Workflow Steps

1. validated retrieval results
2. prompt assembly
3. citation mapping
4. generation request
5. streaming orchestration
6. response persistence

---

## Constraints

Generation must:
- remain grounded
- preserve citations
- remain traceable
- remain observable

---

# Prompt Assembly Workflow

## Objective

Construct secure grounded prompts.

---

## Workflow Steps

1. top-k chunk selection
2. metadata injection
3. citation attachment
4. hallucination traceability metadata insertion
5. prompt construction

---

## Constraints

Prompt assembly must:
- remain deterministic
- preserve chunk identifiers
- preserve document identifiers

---

# Hallucination Scoring Workflow

## Objective

Evaluate grounding quality of generated responses.

---

## Workflow Steps

1. generated response parsing
2. evidence comparison
3. claim grounding evaluation
4. hallucination score calculation
5. confidence classification

---

## Outputs

Produces:
- hallucination score
- unsupported claim indicators
- grounding confidence

---

# Citation Grounding Workflow

## Objective

Ensure every generated claim remains traceable.

---

## Workflow Steps

1. chunk-reference mapping
2. document-reference mapping
3. citation attachment
4. frontend citation rendering

---

## Constraints

Ungrounded claims must remain identifiable.

False citation attribution is prohibited.

---

# Feedback Workflow

## Objective

Collect retrieval quality improvement signals.

---

## Workflow Steps

1. response feedback submission
2. feedback validation
3. retrieval trace persistence
4. evaluation signal storage
5. analytics aggregation

---

## Outputs

Produces:
- retrieval quality metrics
- ranking improvement signals
- evaluation datasets

---

# Audit Workflow

## Objective

Maintain enterprise-grade traceability.

---

## Workflow Steps

1. event capture
2. trace metadata attachment
3. persistence
4. observability integration

---

## Mandatory Audit Coverage

Must audit:
- uploads
- retrieval requests
- generation requests
- permission changes
- admin actions
- RBAC denials

---

# Reindexing Workflow

## Objective

Rebuild sparse retrieval indexes periodically.

---

## Workflow Steps

1. nightly scheduler trigger
2. changed-document detection
3. BM25 index rebuild
4. index validation
5. deployment swap

---

## Constraints

Reindexing must:
- avoid downtime
- preserve tenant isolation
- remain observable

---

# Caching Workflow

## Objective

Reduce repeated retrieval latency.

---

## Workflow Steps

1. query normalization
2. cache lookup
3. RBAC validation
4. cache hit validation
5. cached response delivery

---

## Constraints

Caching must remain:
- tenant-aware
- RBAC-aware
- expiration-controlled

Unsafe cache sharing is prohibited.

---

# Failure Handling Workflow

## Objective

Ensure resilient execution.

---

## Workflow Steps

1. failure detection
2. structured error creation
3. trace attachment
4. observability logging
5. retry handling where applicable

---

## Constraints

Silent failures are prohibited.

---

# Workflow Ordering Principle

Workflow ordering is architecture-governed.

Critical ordering constraints:
- RBAC before generation
- tenant validation before retrieval
- reranking after retrieval
- hallucination scoring after generation

Workflow shortcuts are prohibited.

---

# Repository Alignment

All workflows must remain aligned with:
- SYSTEM_ARCHITECTURE.md
- MODULE_BOUNDARIES.md
- ENGINEERING_INVARIANTS.md
- SECURITY_INVARIANTS.md
- RETRIEVAL_INVARIANTS.md

Workflow behavior is governed by repository intelligence.