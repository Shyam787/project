# TECH STACK

## Purpose

This document defines the official technology stack for the repository.

It explains:
- selected technologies
- architectural responsibilities
- cost strategy
- deployment compatibility
- provider abstraction strategy

Only documented technologies are considered officially supported.

---

# Technology Selection Philosophy

The stack is selected to optimize:
- local-first development
- low operational cost
- production scalability
- open-source compatibility
- modular portability
- CPU-based execution
- enterprise architecture alignment

The project intentionally avoids unnecessary paid dependencies during development.

---

# Backend Stack

## FastAPI

Purpose:
Primary backend framework.

Responsibilities:
- REST APIs
- streaming APIs
- orchestration workflows
- authentication middleware
- retrieval coordination

Why selected:
- async-native
- high performance
- strong typing support
- excellent AI ecosystem compatibility

---

## Python

Purpose:
Primary backend language.

Responsibilities:
- retrieval orchestration
- embedding workflows
- reranking
- hallucination scoring
- infrastructure integration

Why selected:
- strongest AI ecosystem
- mature retrieval tooling
- model ecosystem compatibility

---

# Retrieval Stack

## Qdrant

Purpose:
Vector database.

Responsibilities:
- dense vector storage
- tenant namespace isolation
- vector similarity search

Why selected:
- open-source
- lightweight local deployment
- strong filtering support
- distributed scalability support

Development mode:
- local Docker deployment

Production upgrade path:
- distributed cluster deployment

---

## rank_bm25

Purpose:
Sparse retrieval engine.

Responsibilities:
- keyword retrieval
- lexical matching
- sparse ranking

Why selected:
- lightweight
- local execution
- simple integration
- no infrastructure cost

---

## Reciprocal Rank Fusion (RRF)

Purpose:
Hybrid retrieval fusion.

Responsibilities:
- combine dense and sparse rankings
- improve retrieval robustness

Why selected:
- simple
- effective
- model-independent
- low computational overhead

---

## BGE-M3

Purpose:
Embedding model.

Responsibilities:
- multilingual embeddings
- retrieval embeddings

Why selected:
- CPU-compatible
- strong multilingual retrieval quality
- open-source
- efficient inference

Execution strategy:
- ONNX optimized CPU inference

---

## Cross Encoder (ms-marco)

Purpose:
Reranking model.

Responsibilities:
- rerank top-k retrieved chunks
- improve semantic relevance

Why selected:
- strong retrieval quality
- CPU-compatible inference
- acceptable latency

---

# Generation Stack

## Groq API

Purpose:
LLM inference provider.

Responsibilities:
- response generation
- streaming completion

Why selected:
- generous free tier
- low latency
- simple integration
- suitable for internship-scale deployment

Architecture note:
The repository abstracts LLM providers to support future replacement.

---

# Authentication & RBAC

## Keycloak

Purpose:
Authentication and authorization provider.

Responsibilities:
- SSO
- JWT issuance
- role management
- tenant-aware identity management

Why selected:
- open-source
- enterprise-grade RBAC support
- local deployment support

---

# Persistence Layer

## PostgreSQL

Purpose:
Primary relational database.

Responsibilities:
- metadata storage
- RBAC persistence
- audit logs
- feedback persistence
- tenant metadata

Why selected:
- production reliability
- relational consistency
- strong indexing support

Development strategy:
- local PostgreSQL instance

---

## Redis

Purpose:
Caching layer.

Responsibilities:
- query caching
- temporary state management
- performance optimization

Why selected:
- lightweight
- fast
- widely adopted
- easy Docker deployment

---

# Frontend Stack

## Next.js

Purpose:
Frontend application framework.

Responsibilities:
- dashboard rendering
- streaming chat UI
- admin interfaces
- responsive frontend

Why selected:
- strong React ecosystem
- excellent routing
- SSR support
- production maturity

---

## Tailwind CSS

Purpose:
Styling framework.

Responsibilities:
- responsive layouts
- UI consistency
- rapid styling

Why selected:
- utility-first consistency
- strong developer productivity

---

## shadcn/ui

Purpose:
Component system.

Responsibilities:
- reusable UI components
- consistent frontend design

Why selected:
- modern UI quality
- composable architecture
- Tailwind compatibility

---

# Observability Stack

## Grafana

Purpose:
Monitoring dashboards.

Responsibilities:
- retrieval metrics visualization
- latency dashboards
- hallucination monitoring
- operational observability

Why selected:
- open-source
- production-proven
- lightweight local deployment

---

# Infrastructure Stack

## Docker Compose

Purpose:
Local orchestration.

Responsibilities:
- local multi-service deployment
- development environment management

Why selected:
- local simplicity
- fast setup
- internship-friendly workflow

---

## Kubernetes

Purpose:
Production orchestration.

Responsibilities:
- scalable deployment
- service isolation
- network policy enforcement

Why selected:
- enterprise deployment standard
- production readiness

Development strategy:
- architecture-ready even if local cluster not continuously active

---

## Terraform

Purpose:
Infrastructure-as-code.

Responsibilities:
- reproducible cloud provisioning
- encrypted infrastructure setup

Why selected:
- cloud portability
- reproducible infrastructure management

---

# Cost Strategy

The project prioritizes:
- open-source tooling
- local execution
- CPU inference
- free-tier provider usage

Paid infrastructure is intentionally minimized during development.

---

# Provider Abstraction Strategy

External services must remain replaceable.

Abstracted providers include:
- LLM providers
- file storage providers
- embedding providers
- deployment providers

The architecture avoids hardcoded vendor lock-in.

---

# Deployment Philosophy

The repository supports:
- local-first development
- production-ready architecture
- future cloud portability
- low-cost experimentation

The system is intentionally designed to scale without requiring architectural redesign.