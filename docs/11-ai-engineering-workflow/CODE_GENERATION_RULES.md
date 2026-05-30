# CODE GENERATION RULES

## Purpose

This document defines mandatory coding and implementation standards for all generated code within the repository.

These rules ensure:
- architectural consistency
- maintainability
- observability
- modularity
- production readiness
- implementation stability

All generated code must comply with these standards.

---

# Core Engineering Principles

## Principle 1 — Readability Over Cleverness

Code must prioritize:
- clarity
- maintainability
- explicit behavior
- predictable structure

Complex implicit logic is prohibited.

---

## Principle 2 — Modularity

Each module must:
- own a single responsibility
- expose stable interfaces
- avoid hidden dependencies
- remain independently testable

Cross-module leakage is prohibited.

---

## Principle 3 — Explicitness

Critical behavior must remain explicit.

Examples:
- RBAC enforcement
- tenant validation
- retrieval filtering
- hallucination scoring
- audit logging

Implicit security behavior is prohibited.

---

## Principle 4 — Production Discipline

All code must be production-oriented.

Generated code must include:
- validation
- logging
- structured errors
- observability hooks
- retry handling where required

Prototype-style shortcuts are prohibited.

---

# Backend Standards

## Framework

Backend stack:
- FastAPI
- PostgreSQL
- Redis
- Qdrant
- Keycloak

No unapproved framework substitutions.

---

## Async Discipline

All I/O-heavy operations must use asynchronous execution.

Examples:
- database operations
- API requests
- Redis access
- streaming
- vector retrieval

Blocking operations inside async workflows are prohibited.

---

## Service Architecture

Backend follows modular monolith architecture.

Services must remain separated by responsibility.

Examples:
- auth service
- ingestion service
- retrieval service
- reranking service
- hallucination service
- feedback service

Direct cross-service internal logic coupling is prohibited.

---

# API Standards

## Structured Responses

All APIs must return structured responses.

Response structure must include:
- success state
- payload
- metadata
- error details where applicable

Unstructured responses are prohibited.

---

## Streaming Standards

Streaming APIs must:
- use Server-Sent Events
- support partial token delivery
- preserve citation mapping
- preserve auditability

Streaming must remain observable.

---

## Error Handling

All APIs must:
- return deterministic error formats
- avoid raw exception leakage
- include traceable identifiers

Silent failures are prohibited.

---

# Security Standards

## RBAC Enforcement

RBAC enforcement must occur:
- before reranking
- before prompt assembly
- before generation

Unauthorized chunks must never enter generation context.

---

## Tenant Isolation

Every tenant operation must validate:
- tenant ownership
- namespace boundaries
- document access permissions

Cross-tenant leakage is prohibited.

---

## Secrets Handling

Secrets must never:
- exist in source code
- exist in frontend bundles
- exist in logs

Secrets must be environment-managed.

---

# Retrieval Standards

## Retrieval Pipeline Order

The retrieval pipeline order is fixed:

1. tenant validation
2. RBAC filtering
3. dense retrieval
4. sparse retrieval
5. fusion
6. reranking
7. prompt assembly
8. generation
9. hallucination scoring
10. citation grounding

Pipeline reordering is prohibited.

---

## Retrieval Transparency

Retrieval systems must expose:
- retrieved chunk identifiers
- retrieval scores
- reranking scores
- hallucination scores
- citations

Opaque retrieval behavior is prohibited.

---

# Database Standards

## Schema Discipline

Database schemas must:
- remain normalized where appropriate
- include indexing strategy
- include tenant ownership
- support auditability

Unscoped global records are prohibited.

---

## Migration Discipline

All schema changes must:
- use migrations
- remain reversible
- preserve data integrity

Direct production schema edits are prohibited.

---

# Logging Standards

## Structured Logging

All logs must be structured.

Logs must include:
- timestamps
- tenant identifiers
- request identifiers
- operation identifiers
- error context

Plain console debugging logs are prohibited in production code.

---

## Audit Logging

Critical operations must be audit logged.

Examples:
- document uploads
- retrieval operations
- generation requests
- RBAC denials
- admin actions

Audit logging is mandatory.

---

# Frontend Standards

## Framework

Frontend stack:
- Next.js
- Tailwind CSS
- shadcn/ui

Unapproved UI framework substitutions are prohibited.

---

## Component Discipline

Components must:
- remain reusable
- remain isolated
- avoid duplicated styling logic
- avoid mixed responsibilities

Large monolithic UI components are prohibited.

---

## Responsive Design

Frontend must:
- support desktop-first layouts
- avoid horizontal overflow
- preserve usability across breakpoints

Broken responsive layouts are unacceptable.

---

# Testing Standards

Every major subsystem must include:
- unit tests
- integration tests
- API tests
- RBAC tests
- tenant isolation tests

Critical workflows require end-to-end tests.

---

# Infrastructure Standards

Infrastructure definitions must:
- remain reproducible
- remain environment-configurable
- support local-first deployment
- support future cloud deployment

Hardcoded infrastructure assumptions are prohibited.

---

# AI Generation Constraints

AI-generated code must not:
- invent undocumented architecture
- bypass invariants
- merge unrelated modules
- introduce hidden dependencies
- generate dead code scaffolding

Generated code must align with repository intelligence.

---

# Repository Quality Principle

The repository prioritizes:
- correctness
- maintainability
- observability
- security
- architectural consistency

Implementation speed is secondary to engineering quality.