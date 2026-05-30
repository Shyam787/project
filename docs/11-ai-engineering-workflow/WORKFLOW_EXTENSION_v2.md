# WORKFLOW_EXTENSION_v2

## Purpose

This document is an extension to the existing AI Engineering Workflow.

It defines the **strict execution control layer** for Codex / AI-assisted development and system runtime behavior.

This file is NOT optional. It overrides any ambiguous execution behavior in the system.

---

# Core Principle

The system is not free-form.

It is a **deterministic execution pipeline with enforced stages**.

Any deviation from this order is considered a system design violation.

---

# Universal Execution Pipeline (STRICT ORDER)

Every user request (query, ingestion, retrieval, generation) MUST follow:

## 1. Identity Resolution
- Authenticate user
- Validate JWT (Keycloak)
- Resolve tenant ID
- Resolve role

---

## 2. RBAC Pre-Filter (MANDATORY FIRST SECURITY GATE)
- Fetch allowed document scope
- Apply document-level permissions
- Apply tenant isolation filter

> ❗ No retrieval is allowed before this step

---

## 3. Hybrid Retrieval Execution

Run in parallel:
- Dense retrieval (Qdrant embeddings)
- Sparse retrieval (BM25)

Then:
- Merge using Reciprocal Rank Fusion (RRF)

---

## 4. Cross-Encoder Re-ranking

- Take top-k merged results
- Re-rank using cross-encoder/ms-marco
- Produce final ranked context list

---

## 5. Context Assembly Layer

- Build final context window
- Enforce token budget constraints
- Ensure only RBAC-approved chunks exist

---

## 6. Prompt Construction Layer

- Inject:
  - system rules
  - retrieved context
  - tenant constraints
- Ensure no external leakage

---

## 7. LLM Generation (Groq API)

- Generate response using grounded context only
- No external knowledge expansion allowed unless explicitly permitted

---

## 8. Citation Binding Layer

- Each claim MUST be mapped to:
  - chunk_id
  - document_id
- No uncited claims allowed

---

## 9. Hallucination Scoring Layer

- Evaluate output against retrieved context
- Assign hallucination score (0–1)

Rules:
- > 0.15 → WARNING
- > 0.30 → INVALID RESPONSE FLAG

---

## 10. Response Finalization Layer

- Attach:
  - citations
  - hallucination score badge
  - retrieval trace metadata (internal)

---

# HARD CONSTRAINTS

## RBAC Constraint
- RBAC filtering MUST occur BEFORE retrieval

## Retrieval Constraint
- LLM MUST NEVER see unfiltered data

## Citation Constraint
- No response is valid without citations (except system errors)

## Hallucination Constraint
- Any uncited claim is treated as invalid

## Tenant Constraint
- Cross-tenant data mixing is strictly forbidden

---

# OBSERVABILITY ENFORCEMENT

Every stage MUST emit:

- trace_id
- latency_ms
- stage_name

Required stages:
- auth_latency
- retrieval_latency
- rerank_latency
- generation_latency

---

# CACHING RULES

- Cache is applied ONLY after RBAC filtering
- Cache keys MUST include:
  - tenant_id
  - user_role
  - query hash

---

# FAILURE HANDLING RULES

If any stage fails:

- STOP pipeline execution
- Log failure stage
- Return safe fallback response

---

# SECURITY GUARANTEE MODEL

System guarantees:

- No unauthorized document exposure
- No cross-tenant leakage
- No LLM access to restricted data
- No citation spoofing

---

# CODEx EXECUTION RULE (IMPORTANT)

When Codex generates or modifies code:

It MUST follow:

1. Read all architecture docs first
2. Identify affected pipeline stage
3. Apply changes ONLY within correct stage boundary
4. Never bypass RBAC or retrieval ordering rules
5. Preserve observability hooks

---

# DEVELOPMENT CONSTRAINT

Codex is NOT allowed to:
- change execution order
- skip RBAC enforcement
- bypass reranking
- ignore hallucination scoring
- remove tracing

---

# SYSTEM BEHAVIOR MODEL

System is defined as:
Secure Retrieval-Augmented Generation Pipeline
with enforced RBAC + deterministic execution + observability
---

# GOVERNANCE RULE

This file acts as:

> The execution brain of the system

Any conflict with other docs:
- this file takes priority for runtime execution flow

---

# VERSION CONTROL

- Version: v2
- Status: ACTIVE
- Type: EXECUTION CONTROL LAYER