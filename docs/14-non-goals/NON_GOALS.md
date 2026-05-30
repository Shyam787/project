# NON_GOALS

## Purpose

This document defines explicit non-goals of the Enterprise RAG system.

It ensures:
- scope control during development
- prevention of feature creep
- clarity for Codex-based implementation
- evaluation boundary enforcement

---

# Core Philosophy

Anything NOT explicitly required in project statement or architecture:

> is NOT part of the system

---

# NON-GOALS LIST

## 1. No Fine-Tuning of LLMs

The system will NOT:
- fine-tune any large language model
- train custom foundation models
- modify Groq LLM internals

Reason:
- cost heavy
- unnecessary for RAG-based architecture

---

## 2. No Custom Vector DB Implementation

The system will NOT:
- build its own vector database
- replace Qdrant with custom ANN implementation

Reason:
- Qdrant already satisfies requirements

---

## 3. No Distributed Microservices Architecture (Initial Phase)

The system will NOT:
- start as microservices
- deploy distributed service mesh

Reason:
- modular monolith is chosen for stability

---

## 4. No Real Payment System

The system will NOT:
- include billing systems
- include subscription handling
- integrate payment gateways

---

## 5. No External Data Scraping

The system will NOT:
- crawl web data automatically
- scrape external websites for ingestion

Only user-uploaded documents are allowed.

---

## 6. No Multi-Model Ensemble Complexity

The system will NOT:
- use multiple competing LLMs
- implement model voting systems

Only Groq API LLM is used.

---

## 7. No Real-Time Collaborative Editing

The system will NOT:
- support Google-doc style collaboration
- include real-time multi-user editing of documents

---

## 8. No Offline LLM Hosting

The system will NOT:
- host local LLM models (LLaMA, Mistral, etc.)
- run inference locally

---

## 9. No Advanced AI Agents

The system will NOT:
- implement autonomous agent loops
- allow recursive self-decision systems

All behavior is pipeline-controlled.

---

## 10. No Multi-Region Active Deployment

The system will NOT:
- deploy across multiple geographic regions
- implement global load balancing

---

# STRICT SYSTEM BOUNDARY

The system is ONLY:

> Enterprise Multi-Tenant Retrieval-Augmented Generation Platform

---

# WHAT THE SYSTEM DOES DO

For clarity, it DOES:

- multi-tenant document ingestion
- hybrid retrieval (BM25 + vector)
- reranking (cross-encoder)
- RBAC enforcement
- hallucination scoring
- citation grounding
- observability tracking
- enterprise UI dashboards

---

# GOVERNANCE RULE

Any feature not listed in:

- architecture docs
- ADRs
- roadmap

is automatically OUT OF SCOPE.

---

# CODEx ENFORCEMENT RULE

Codex MUST:
- reject implementation of non-goals
- avoid feature expansion
- strictly follow documented scope

---

# FINAL STATEMENT

This system is intentionally constrained to ensure:

- reliability
- evaluability
- production readiness
- deterministic behavior