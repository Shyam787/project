# DOCUMENT USAGE PROTOCOL

## Purpose

This document defines:
- document ownership
- authoritative source mapping
- cross-document dependency rules
- reference discipline
- conflict resolution strategy

This protocol prevents:
- duplicated ownership
- architectural contradictions
- AI-generated implementation drift
- inconsistent terminology

All contributors and AI-assisted workflows must follow this protocol.

---

# Ownership Principle

Every architectural concern has exactly one authoritative source document.

Documents may reference concepts owned by other documents but may not redefine them.

---

# Source of Truth Mapping

## Project Identity

| Topic | Authoritative Document |
|---|---|
| project purpose | PROJECT_OVERVIEW.md |
| project scope | PROJECT_SCOPE.md |
| stack selection | TECH_STACK.md |

---

## Architecture

| Topic | Authoritative Document |
|---|---|
| system architecture | SYSTEM_ARCHITECTURE.md |
| module boundaries | MODULE_BOUNDARIES.md |
| workflows | SYSTEM_WORKFLOWS.md |
| provider abstraction | PROVIDER_ABSTRACTIONS.md |
| multi-tenancy | MULTI_TENANCY_STRATEGY.md |

---

## Engineering Constraints

| Topic | Authoritative Document |
|---|---|
| global invariants | ENGINEERING_INVARIANTS.md |
| security invariants | SECURITY_INVARIANTS.md |
| retrieval invariants | RETRIEVAL_INVARIANTS.md |
| UI invariants | UI_INVARIANTS.md |

---

## Retrieval System

| Topic | Authoritative Document |
|---|---|
| retrieval pipeline | RETRIEVAL_PIPELINE.md |
| chunking | CHUNKING_STRATEGY.md |
| hybrid search | HYBRID_SEARCH.md |
| reranking | RERANKING_STRATEGY.md |
| hallucination scoring | HALLUCINATION_SCORING.md |
| citation grounding | CITATION_GROUNDING.md |
| feedback learning | FEEDBACK_LOOP.md |

---

## Security & RBAC

| Topic | Authoritative Document |
|---|---|
| authentication | AUTHENTICATION_FLOW.md |
| RBAC | RBAC_MODEL.md |
| tenant isolation | TENANT_ISOLATION.md |
| DPDP handling | PII_DPDP_STRATEGY.md |
| audit logging | AUDIT_LOGGING.md |

---

## Persistence Layer

| Topic | Authoritative Document |
|---|---|
| relational schema | POSTGRES_SCHEMA.md |
| vector schema | QDRANT_SCHEMA.md |
| caching | REDIS_CACHING.md |
| metadata | DOCUMENT_METADATA.md |

---

## API Layer

| Topic | Authoritative Document |
|---|---|
| API conventions | API_STANDARDS.md |
| auth APIs | AUTH_APIS.md |
| document APIs | DOCUMENT_APIS.md |
| chat APIs | CHAT_APIS.md |
| streaming | STREAMING_PROTOCOL.md |
| errors | ERROR_HANDLING.md |

---

## Infrastructure

| Topic | Authoritative Document |
|---|---|
| Docker setup | DOCKER_COMPOSE_SETUP.md |
| Kubernetes | KUBERNETES_ARCHITECTURE.md |
| network isolation | NETWORK_POLICIES.md |
| Terraform | TERRAFORM_INFRA.md |
| residency | DATA_RESIDENCY.md |

---

## Observability

| Topic | Authoritative Document |
|---|---|
| metrics | METRICS_STRATEGY.md |
| dashboards | GRAFANA_DASHBOARDS.md |
| latency | LATENCY_TRACKING.md |
| alerting | ALERTING_RULES.md |

---

## Testing & Evaluation

| Topic | Authoritative Document |
|---|---|
| testing | TESTING_STRATEGY.md |
| evaluation dataset | EVALUATION_DATASET.md |
| RBAC testing | RBAC_TEST_CASES.md |
| hallucination testing | HALLUCINATION_TESTS.md |

---

## UI/UX

| Topic | Authoritative Document |
|---|---|
| UI rules | UI_SYSTEM_GUIDELINES.md |
| component system | COMPONENT_ARCHITECTURE.md |
| responsiveness | RESPONSIVE_RULES.md |

---

# Cross-Document Dependency Rules

## Foundation Dependency Rule

All specialized documents depend on:
- SYSTEM_ARCHITECTURE.md
- ENGINEERING_INVARIANTS.md

These documents must always be treated as globally authoritative.

---

## Retrieval Dependency Rule

Retrieval documents depend on:
- SYSTEM_ARCHITECTURE.md
- MULTI_TENANCY_STRATEGY.md
- RETRIEVAL_INVARIANTS.md

---

## Security Dependency Rule

Security documents depend on:
- ENGINEERING_INVARIANTS.md
- SECURITY_INVARIANTS.md
- MULTI_TENANCY_STRATEGY.md

---

## Infrastructure Dependency Rule

Infrastructure documents depend on:
- SYSTEM_ARCHITECTURE.md
- SECURITY_INVARIANTS.md
- TENANT_ISOLATION.md

---

# Conflict Resolution Rules

## Rule 1 — Higher Authority Wins

If documents conflict:
- higher hierarchy level dominates

Priority order:
1. orchestration layer
2. foundation layer
3. specialized systems
4. infrastructure
5. implementation details

---

## Rule 2 — Invariants Override All

Engineering invariants are globally binding.

No subsystem may violate:
- tenant isolation
- RBAC enforcement
- auditability
- citation grounding

---

## Rule 3 — No Duplicate Ownership

Documents must not redefine topics owned elsewhere.

Instead:
- reference authoritative documents conceptually
- extend only subsystem-specific behavior

---

# Repository Reference Discipline

## Allowed References

Documents may:
- reference workflows
- reference architecture
- reference constraints

without redefining them.

---

## Prohibited References

Documents must not:
- redefine ownership
- duplicate schema definitions
- redefine invariants
- bypass hierarchy

---

# AI Context Loading Discipline

AI-assisted workflows must:
- load authoritative documents first
- resolve dependencies before implementation
- prioritize higher-authority documents
- avoid isolated interpretation of subsystem docs

---

# Governance Principle

The repository is treated as:
- deterministic
- hierarchical
- constraint-driven

Implementation must follow documented intelligence rather than improvisation.