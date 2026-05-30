# REDIS_CACHING

## Purpose

This document defines the authoritative Redis caching strategy for the platform.

It governs:
- query caching
- retrieval caching
- response caching
- cache isolation
- cache invalidation
- cache observability

All caching implementation must comply with this strategy.

---

# Caching Philosophy

Caching exists to improve:
- response latency
- retrieval efficiency
- system scalability
- repeated query performance

Caching must never compromise:
- tenant isolation
- RBAC security
- retrieval correctness

---

# Core Objectives

The caching layer must:
- reduce repeated computation
- reduce repeated retrieval latency
- reduce repeated reranking overhead
- remain tenant-aware
- remain RBAC-aware

---

# Redis Responsibilities

Redis stores:
- query cache
- retrieval cache
- session cache
- temporary workflow state
- rate limit state

Redis is not the authoritative source of truth.

---

# Cache Categories

The platform supports:

1. Query Response Cache
2. Embedding Cache
3. Retrieval Cache
4. Session Cache
5. Rate Limiting Cache

---

# Query Response Cache

## Responsibilities

Stores:
- repeated query responses
- retrieval traces
- citation metadata

---

## Cache Window

Recommended TTL:

```text
10 minutes