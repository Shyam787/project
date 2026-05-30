# SYSTEM ARCHITECTURE

## Purpose

This document defines the authoritative high-level architecture for the entire platform.

It governs:
- system structure
- service responsibilities
- subsystem interactions
- data flow
- security boundaries
- deployment boundaries
- operational architecture

All subsystem implementations must comply with this architecture.

---

# Architectural Philosophy

The platform follows a modular enterprise RAG architecture optimized for:
- security
- tenant isolation
- retrieval quality
- observability
- infrastructure portability
- low-cost local development
- future production scalability

The architecture prioritizes:
- deterministic workflows
- explicit security enforcement
- modular responsibilities
- provider abstraction
- operational transparency

---

# High-Level System Overview

The platform consists of the following major layers:

1. Frontend Layer
2. API & Orchestration Layer
3. Authentication & RBAC Layer
4. Retrieval Layer
5. Generation Layer
6. Persistence Layer
7. Observability Layer
8. Infrastructure Layer

Each layer owns clearly separated responsibilities.

---

# Frontend Layer

## Responsibilities

The frontend layer provides:
- document management
- chat interface
- RBAC administration
- observability dashboards
- audit log exploration

---

## Major Frontend Modules

### Document Management Portal

Responsibilities:
- upload documents
- assign metadata
- assign permissions
- monitor ingestion status

---

### Chat Interface

Responsibilities:
- streaming responses
- citation visualization
- hallucination visibility
- conversation interaction

---

### RBAC Administration Panel

Responsibilities:
- user-role management
- permission assignment
- tenant administration

---

### Observability Dashboard

Responsibilities:
- retrieval metrics
- latency metrics
- hallucination trends
- feedback analytics

---

# API & Orchestration Layer

## Responsibilities

This layer coordinates:
- ingestion workflows
- retrieval workflows
- generation workflows
- caching
- observability instrumentation

This layer is implemented using FastAPI.

---

## Major Backend Modules

### API Gateway Layer

Responsibilities:
- request validation
- authentication enforcement
- tenant resolution
- request tracing

---

### Ingestion Service

Responsibilities:
- document parsing
- chunking
- embedding orchestration
- sparse indexing
- metadata persistence

---

### Retrieval Service

Responsibilities:
- dense retrieval
- sparse retrieval
- fusion
- retrieval scoring

---

### Reranking Service

Responsibilities:
- cross-encoder reranking
- top-k refinement
- retrieval prioritization

---

### Generation Service

Responsibilities:
- prompt assembly
- streaming generation
- citation mapping
- hallucination scoring

---

### Feedback Service

Responsibilities:
- feedback collection
- retrieval evaluation persistence
- ranking improvement support

---

### Audit Service

Responsibilities:
- audit persistence
- query traceability
- retrieval traceability
- security event logging

---

# Authentication & RBAC Layer

## Responsibilities

This layer provides:
- authentication
- authorization
- tenant identity management
- access validation

---

## Keycloak Responsibilities

Keycloak manages:
- login flows
- JWT issuance
- role management
- tenant-aware identities

---

## RBAC Enforcement Architecture

RBAC enforcement occurs:
- before retrieval finalization
- before reranking
- before generation

Unauthorized chunks must never:
- reach reranking
- reach prompts
- appear in citations

---

# Retrieval Layer

## Responsibilities

The retrieval layer provides:
- dense retrieval
- sparse retrieval
- hybrid ranking
- reranking orchestration

---

# Dense Retrieval Subsystem

## Technology

Qdrant

## Responsibilities

- vector storage
- vector search
- tenant namespace isolation

---

# Sparse Retrieval Subsystem

## Technology

BM25

## Responsibilities

- lexical matching
- keyword search
- sparse ranking

---

# Hybrid Retrieval Architecture

The retrieval workflow is:

1. dense retrieval
2. sparse retrieval
3. reciprocal rank fusion
4. RBAC validation
5. reranking
6. top-k selection

Hybrid retrieval improves:
- semantic relevance
- keyword recall
- enterprise search quality

---

# Reranking Layer

## Technology

Cross encoder

## Responsibilities

- semantic refinement
- ranking correction
- retrieval prioritization

Only authorized chunks enter reranking.

---

# Generation Layer

## Responsibilities

The generation layer provides:
- grounded generation
- streaming responses
- hallucination scoring
- citation generation

---

# Prompt Assembly Workflow

Prompt assembly includes:
- retrieved chunk selection
- citation mapping
- metadata injection
- hallucination traceability

Prompt assembly occurs only after:
- RBAC validation
- tenant validation
- retrieval filtering

---

# Hallucination Scoring Architecture

Hallucination scoring compares:
- generated claims
- retrieved evidence
- citation coverage

The system exposes hallucination visibility to users.

---

# Citation Architecture

Each generated claim must:
- reference source chunks
- reference source documents
- remain traceable

Citations are first-class system artifacts.

---

# Persistence Layer

The platform uses multiple persistence systems.

---

# PostgreSQL Responsibilities

Stores:
- metadata
- users
- permissions
- audit logs
- feedback
- ingestion status

---

# Qdrant Responsibilities

Stores:
- embeddings
- vector metadata
- tenant namespaces

---

# Redis Responsibilities

Stores:
- cached queries
- temporary streaming state
- performance caches

---

# Observability Layer

## Responsibilities

The observability layer provides:
- metrics
- tracing
- dashboards
- latency monitoring
- hallucination tracking

---

# Metrics Categories

Tracked metrics include:
- retrieval latency
- reranking latency
- generation latency
- hallucination rate
- cache hit ratio
- feedback metrics

---

# Auditability

Every critical workflow must remain auditable.

Audit coverage includes:
- uploads
- retrieval operations
- RBAC denials
- generation requests
- feedback submissions

---

# Infrastructure Layer

## Responsibilities

Infrastructure supports:
- local development
- scalable deployment
- environment isolation
- deployment reproducibility

---

# Local Development Architecture

Uses:
- Docker Compose
- local PostgreSQL
- local Qdrant
- local Redis
- local Keycloak

Optimized for:
- zero-cost development
- CPU-based inference
- internship-scale workflows

---

# Production Architecture

Uses:
- Kubernetes
- Terraform
- encrypted storage
- network policies
- distributed scalability

Production infrastructure remains architecture-compatible with local development.

---

# Network Isolation Principles

Critical services must not be publicly exposed.

Protected services:
- PostgreSQL
- Qdrant
- Redis

Access occurs only through internal networking.

---

# Security Boundaries

Critical security boundaries include:
- tenant isolation
- namespace isolation
- RBAC enforcement
- API authentication
- internal-only infrastructure access

Security enforcement is architecture-level, not implementation-level.

---

# Data Flow Overview

## Ingestion Flow

1. upload document
2. parse document
3. chunk document
4. generate embeddings
5. generate sparse index
6. persist metadata
7. store vectors
8. assign permissions

---

## Query Flow

1. authenticate user
2. resolve tenant
3. validate permissions
4. execute hybrid retrieval
5. apply RBAC filtering
6. rerank results
7. assemble prompt
8. generate response
9. generate citations
10. score hallucination risk
11. stream response

---

# Architectural Constraints

The following constraints are mandatory:

- RBAC before generation
- no cross-tenant leakage
- citations mandatory
- hallucination visibility mandatory
- observability mandatory
- audit logging mandatory

These constraints are globally binding.

---

# Scalability Philosophy

The architecture supports future scaling through:
- modular services
- provider abstraction
- distributed Qdrant
- Kubernetes orchestration
- infrastructure-as-code

The local-first architecture must remain production-portable.

---

# Repository Alignment

All implementation must align with:
- engineering invariants
- orchestration layer governance
- subsystem ownership rules
- validation requirements

Architecture drift is prohibited.