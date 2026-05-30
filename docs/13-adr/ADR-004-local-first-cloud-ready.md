# ADR-004: LOCAL-FIRST, CLOUD-READY DEPLOYMENT STRATEGY

## Status
Accepted

---

## Context

The system must be developed under constraints:

- minimal or zero cost during development
- internship-level execution environment
- production-grade deployment readiness required
- support for future cloud scaling

We need a deployment strategy that satisfies both:

> local development simplicity + cloud production readiness

---

## Decision

We adopt a:

> Local-first development architecture with cloud-ready abstraction layer

---

## Reasoning

### 1. Cost Constraints

During development:
- no paid cloud infrastructure should be required
- all services must run locally via Docker Compose

This includes:
- PostgreSQL
- Qdrant
- Redis
- Keycloak
- Grafana

---

### 2. Developer Velocity

Local-first ensures:
- fast iteration cycles
- no deployment delays
- deterministic environment setup
- easy debugging

---

### 3. Production Parity

Even though local-first, the system must mirror production:

- same service boundaries
- same API contracts
- same data flow architecture

This ensures zero redesign when moving to cloud.

---

### 4. Cloud Abstraction Layer

All external dependencies must be abstracted:

- vector DB (Qdrant)
- LLM provider (Groq API)
- authentication (Keycloak)
- storage (local now → cloud later)

Interfaces must remain interchangeable.

---

## Architecture Model
Local Mode:
Docker Compose Stack (Full System)

Cloud Mode:
Kubernetes + Managed Services


---

## Service Mapping

| Component | Local | Cloud Future |
|----------|------|-------------|
| Postgres | Local Docker | Managed DB |
| Qdrant | Local container | Distributed cluster |
| Redis | Local container | Managed Redis |
| Keycloak | Local container | Identity provider |
| Grafana | Local container | Cloud observability |

---

## Design Rules

### 1. No Hardcoded Infrastructure
- all services must use environment variables

### 2. Provider Abstraction Required
- LLM provider must be swappable
- storage must be swappable
- retrieval backend must be swappable

### 3. Stateless Backend Design
- backend must remain stateless
- all state stored in external services

---

## Consequences

### Positive

- zero-cost development
- easy onboarding
- consistent architecture
- production readiness from day one

---

### Negative

- requires strict environment discipline
- abstraction overhead during development

---

## Deployment Strategy

### Phase 1: Local Development
- Docker Compose stack
- single-machine execution

### Phase 2: Production Migration
- Kubernetes deployment
- cloud service substitution
- Terraform-based infrastructure

---

## Failure Scenarios Prevented

This ADR prevents:

- vendor lock-in
- cloud dependency during development
- inconsistent environments
- production rewrite effort

---

## Related ADRs

- ADR-001: Modular monolith architecture
- ADR-002: RBAC-before-rerank enforcement
- ADR-003: Qdrant per-tenant isolation