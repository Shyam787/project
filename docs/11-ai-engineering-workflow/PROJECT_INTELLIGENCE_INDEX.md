# PROJECT INTELLIGENCE INDEX

## Purpose

This document is the root orchestration layer for the entire repository intelligence system.

It defines:
- document hierarchy
- authority order
- ownership boundaries
- dependency relationships
- implementation sequencing
- context loading discipline
- architectural governance rules

All AI-assisted implementation workflows must begin by reading this document.

This document is the highest-level routing layer for Codex and all future contributors.

---

# Repository Intelligence Philosophy

The repository is designed as a structured engineering intelligence system rather than a collection of disconnected documentation files.

Documents are intentionally layered and hierarchical.

Higher-priority documents constrain lower-priority documents.

Lower-level implementation documents must never redefine architectural decisions established in higher-level documents.

---

# Intelligence Hierarchy

The repository follows the hierarchy below.

## Level 0 — Orchestration Layer

Purpose:
Controls how repository intelligence is interpreted and consumed.

Documents:

- PROJECT_INTELLIGENCE_INDEX.md
- DOCUMENT_USAGE_PROTOCOL.md
- AI_ENGINEERING_WORKFLOW.md
- CODE_GENERATION_RULES.md
- IMPLEMENTATION_VALIDATION.md

Authority:
Highest operational authority.

These documents govern:
- implementation discipline
- context loading
- engineering workflow
- repository governance

---

## Level 1 — Foundation Layer

Purpose:
Defines project identity, architecture, and non-negotiable engineering constraints.

Folders:
- docs/00-overview/
- docs/01-architecture/
- docs/02-engineering-invariants/

Authority:
Highest architectural authority.

These documents define:
- enterprise problem scope
- system architecture
- invariants
- module boundaries
- tenant isolation guarantees

No lower-level document may override foundation-layer decisions.

---

## Level 2 — Specialized System Layer

Purpose:
Defines behavior for specialized systems.

Folders:
- docs/03-retrieval-system/
- docs/04-security-rbac/
- docs/05-database-design/
- docs/06-api-contracts/

Authority:
Subsystem authority.

These documents define:
- retrieval behavior
- RBAC behavior
- persistence models
- API contracts

Specialized documents must comply with:
- foundation-layer architecture
- engineering invariants
- orchestration-layer governance

---

## Level 3 — Infrastructure & Operations Layer

Purpose:
Defines deployment, observability, monitoring, and operational architecture.

Folders:
- docs/07-infrastructure-devops/
- docs/08-observability/

Authority:
Operational authority.

These documents define:
- Docker deployment
- Kubernetes deployment
- Terraform infrastructure
- monitoring
- metrics
- alerting
- scaling

Infrastructure decisions must comply with:
- security invariants
- tenant isolation requirements
- DPDP compliance rules

---

## Level 4 — Validation & UX Layer

Purpose:
Defines testing methodology, evaluation strategy, UI standards, and implementation execution planning.

Folders:
- docs/09-testing-evaluation/
- docs/10-ui-ux-system/
- docs/12-implementation-roadmap/
- docs/13-adr/
- docs/14-non-goals/

Authority:
Validation and governance authority.

These documents define:
- testing
- evaluation
- frontend standards
- ADR decisions
- non-goals
- implementation sequencing

---

# Repository Authority Rules

## Rule 1 — Higher Layers Dominate Lower Layers

Lower-level documents may refine behavior but may never override higher-level constraints.

Example:
- retrieval logic may not violate engineering invariants
- APIs may not bypass RBAC constraints
- infrastructure may not violate DPDP requirements

---

## Rule 2 — Invariants Are Absolute

Engineering invariants are globally authoritative.

No implementation may violate:
- tenant isolation
- RBAC enforcement
- citation grounding
- hallucination scoring requirements
- audit logging requirements

---

## Rule 3 — Ownership Is Explicit

Every topic has a single authoritative source document.

Topic ownership is defined in:
- DOCUMENT_USAGE_PROTOCOL.md

Duplicate ownership is prohibited.

---

## Rule 4 — Architecture Stability

Architecture changes are controlled.

Major architectural modifications require:
- explicit review
- ADR documentation
- dependency validation

Architecture must not drift during implementation.

---

# Mandatory Read Order

All implementation workflows must follow this read hierarchy.

## Before Any Implementation

Required reading order:

1. PROJECT_INTELLIGENCE_INDEX.md
2. DOCUMENT_USAGE_PROTOCOL.md
3. AI_ENGINEERING_WORKFLOW.md
4. ENGINEERING_INVARIANTS.md
5. SYSTEM_ARCHITECTURE.md

No implementation may begin before these documents are understood.

---

# Subsystem Read Requirements

## Retrieval System Work

Required reading:

- ENGINEERING_INVARIANTS.md
- SYSTEM_ARCHITECTURE.md
- RETRIEVAL_PIPELINE.md
- HYBRID_SEARCH.md
- RERANKING_STRATEGY.md

---

## Security Work

Required reading:

- ENGINEERING_INVARIANTS.md
- SECURITY_INVARIANTS.md
- RBAC_MODEL.md
- TENANT_ISOLATION.md
- AUTHENTICATION_FLOW.md

---

## Infrastructure Work

Required reading:

- SYSTEM_ARCHITECTURE.md
- SECURITY_INVARIANTS.md
- KUBERNETES_ARCHITECTURE.md
- NETWORK_POLICIES.md
- TERRAFORM_INFRA.md

---

## Frontend Work

Required reading:

- API_STANDARDS.md
- UI_SYSTEM_GUIDELINES.md
- COMPONENT_ARCHITECTURE.md
- RESPONSIVE_RULES.md

---

# Implementation Sequencing

The project implementation order is fixed.

## Phase 1 — Foundation
- architecture
- invariants
- workflow governance

## Phase 2 — Core Backend
- authentication
- ingestion
- retrieval
- RBAC
- citations

## Phase 3 — APIs & Persistence
- API contracts
- database integration
- caching

## Phase 4 — Frontend
- dashboards
- chat interface
- admin interfaces

## Phase 5 — Observability & Evaluation
- metrics
- dashboards
- hallucination tracking
- evaluation systems

## Phase 6 — Deployment & Hardening
- Kubernetes
- Terraform
- network policies
- production readiness

---

# Repository Governance Rules

## Frozen Architecture Principle

Once a document batch is finalized:
- changes are minimized
- architectural drift is prohibited
- modifications require validation

---

## ADR Requirement

The following changes require ADR entries:
- architecture redesign
- storage redesign
- retrieval redesign
- security redesign
- deployment redesign

---

## No Hidden Logic Principle

All critical system behavior must exist explicitly in documentation.

Critical behavior must never exist only in implementation code.

---

# AI-Assisted Engineering Governance

Codex and all AI-assisted workflows must:
- follow repository hierarchy
- respect authoritative ownership
- obey engineering invariants
- maintain implementation sequencing
- avoid architectural improvisation

Repository intelligence is deterministic and constraint-driven.

Implementation generation must remain aligned with documented architecture at all times.