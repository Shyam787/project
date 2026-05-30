# POSTGRES_SCHEMA

## Purpose

This document defines the authoritative PostgreSQL schema strategy for the platform.

It governs:
- relational data modeling
- tenant-aware schemas
- RBAC persistence
- audit persistence
- metadata persistence
- operational consistency

All database implementation must comply with this strategy.

---

# Database Philosophy

PostgreSQL is the authoritative relational source of truth for:
- users
- tenants
- document metadata
- permissions
- feedback
- audit logs
- operational state

Qdrant stores embeddings.

PostgreSQL stores governance and business data.

---

# Core Objectives

The PostgreSQL layer must:
- remain tenant-aware
- preserve relational integrity
- support RBAC
- support auditability
- support observability
- remain cloud-portable

---

# Database Responsibilities

PostgreSQL stores:
- tenant metadata
- user metadata
- document metadata
- permissions
- ingestion state
- feedback data
- audit logs
- hallucination metadata

---

# Multi-Tenant Strategy

All protected tables must include:
- tenant_id

Queries without tenant filtering are prohibited.

---

# Core Tables

The platform requires:

1. tenants
2. users
3. roles
4. documents
5. document_permissions
6. chunks
7. conversations
8. messages
9. feedback
10. audit_logs
11. hallucination_results

---

# Tenants Table

## Responsibilities

Stores:
- tenant identity
- configuration
- operational metadata

---

## Required Fields

```text
id
name
slug
created_at
updated_at