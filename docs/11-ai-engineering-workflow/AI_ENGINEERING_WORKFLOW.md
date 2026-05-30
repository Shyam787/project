# AI ENGINEERING WORKFLOW

## Purpose

This document defines the operational workflow for AI-assisted engineering within the repository.

It governs:
- Codex implementation behavior
- implementation sequencing
- context loading strategy
- engineering discipline
- validation flow
- architectural consistency

This workflow is mandatory for all AI-assisted implementation tasks.

---

# Engineering Philosophy

The repository follows a constraint-driven engineering model.

AI systems are implementation assistants, not autonomous architects.

Architecture, invariants, and ownership boundaries defined in repository intelligence documents are authoritative and must not be overridden during implementation.

Implementation quality is prioritized over implementation speed.

---

# AI-Assisted Engineering Principles

## Principle 1 — Architecture First

Implementation must always follow documented architecture.

No implementation may:
- redesign architecture implicitly
- bypass module boundaries
- introduce undocumented dependencies
- create hidden workflows

---

## Principle 2 — Invariants Are Mandatory

All engineering invariants are globally binding.

No implementation may violate:
- tenant isolation
- RBAC enforcement
- retrieval security
- citation grounding
- audit logging
- DPDP compliance requirements

---

## Principle 3 — Deterministic Engineering

Implementation must remain:
- deterministic
- modular
- explicit
- traceable
- observable

Implicit logic and hidden system behavior are prohibited.

---

## Principle 4 — Modular Implementation

All implementation must follow defined module boundaries.

Modules must:
- own clear responsibilities
- avoid cross-layer leakage
- expose stable interfaces
- remain independently testable

---

# AI Context Loading Workflow

## Global Mandatory Read Sequence

Before beginning any implementation task, AI workflows must load:

1. PROJECT_INTELLIGENCE_INDEX.md
2. DOCUMENT_USAGE_PROTOCOL.md
3. ENGINEERING_INVARIANTS.md
4. SYSTEM_ARCHITECTURE.md
5. Relevant subsystem documents

Implementation without foundational context is prohibited.

---

# Context Resolution Strategy

## Phase 1 — Global Context

Load:
- architecture
- invariants
- ownership hierarchy

Purpose:
Understand system-wide constraints.

---

## Phase 2 — Subsystem Context

Load:
- subsystem-specific documents
- related API contracts
- persistence rules
- workflow definitions

Purpose:
Understand subsystem behavior.

---

## Phase 3 — Implementation Context

Load:
- coding standards
- validation rules
- testing requirements

Purpose:
Ensure implementation consistency.

---

# Implementation Workflow

All implementation tasks must follow the workflow below.

---

## Step 1 — Context Resolution

Before writing code:
- load authoritative documents
- resolve dependencies
- identify applicable invariants
- identify ownership boundaries

No code generation may begin before context resolution completes.

---

## Step 2 — Dependency Validation

Validate:
- architecture alignment
- module ownership
- API dependencies
- infrastructure compatibility
- security constraints

Undocumented dependencies are prohibited.

---

## Step 3 — Implementation Planning

Before implementation:
- define module responsibility
- define interfaces
- define validation requirements
- define observability requirements
- define testing requirements

Implementation planning must occur before coding.

---

## Step 4 — Controlled Implementation

Implementation must:
- follow architecture
- follow coding standards
- remain modular
- remain observable
- remain testable

No uncontrolled code generation is permitted.

---

## Step 5 — Validation

After implementation:
- validate against invariants
- validate against architecture
- validate RBAC behavior
- validate tenant isolation
- validate observability
- validate API consistency

Validation is mandatory before implementation acceptance.

---

# Implementation Sequencing Rules

The repository implementation sequence is fixed.

---

## Phase 1 — Foundation

Includes:
- project configuration
- architecture scaffolding
- authentication foundation
- database foundation
- infrastructure scaffolding

No advanced features before foundation stabilization.

---

## Phase 2 — Ingestion & Retrieval

Includes:
- document ingestion
- chunking
- embeddings
- vector indexing
- BM25 indexing
- retrieval orchestration

Retrieval implementation must remain isolated from generation logic.

---

## Phase 3 — Security Enforcement

Includes:
- RBAC filtering
- tenant isolation
- access validation
- audit logging
- DPDP controls

Security enforcement occurs before generation.

---

## Phase 4 — Generation Pipeline

Includes:
- reranking
- prompt assembly
- generation
- hallucination scoring
- citation grounding

Generation is downstream of security validation.

---

## Phase 5 — APIs & Frontend

Includes:
- streaming APIs
- dashboards
- admin interfaces
- retrieval monitoring
- frontend UX

Frontend implementation must consume stable APIs.

---

## Phase 6 — Observability & Hardening

Includes:
- metrics
- tracing
- Grafana dashboards
- alerting
- infrastructure hardening

Production readiness is finalized only after observability completion.

---

# Architecture Governance Rules

## No Implicit Architecture Changes

Implementation may not:
- introduce new services
- introduce new infrastructure patterns
- redesign workflows
- redefine ownership

Major changes require ADR review.

---

## No Hidden Security Logic

Security behavior must be:
- explicit
- documented
- testable
- observable

Hidden access-control logic is prohibited.

---

## No Retrieval Bypass

Generation systems must never bypass:
- RBAC filtering
- tenant isolation
- retrieval validation

Unauthorized chunks must never reach LLM prompts.

---

# Testing Discipline

Every major subsystem must include:
- unit tests
- integration tests
- RBAC tests
- tenant isolation tests
- API validation tests

Critical workflows require end-to-end validation.

---

# Observability Discipline

Every major subsystem must expose:
- structured logs
- metrics
- latency measurements
- failure visibility

Opaque execution paths are prohibited.

---

# Frontend Engineering Discipline

Frontend systems must:
- remain responsive
- maintain layout stability
- support streaming UX
- expose citations clearly
- maintain accessibility
- avoid inconsistent component behavior

Broken UI states are unacceptable.

---

# AI-Assisted Engineering Constraints

AI systems must not:
- improvise architecture
- bypass invariants
- merge unrelated responsibilities
- introduce unreviewed dependencies
- generate undocumented workflows

AI systems operate within repository-defined constraints.

---

# Repository Stability Principle

The repository is treated as:
- architecture-driven
- governance-controlled
- implementation-disciplined

All implementation must remain aligned with repository intelligence at all times.