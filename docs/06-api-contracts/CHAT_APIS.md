# CHAT_APIS

## Purpose

This document defines the authoritative chat and generation API contracts for the platform.

It governs:
- question answering workflows
- retrieval orchestration
- streaming responses
- citation delivery
- hallucination scoring
- conversational traceability

All chat API implementation must comply with this strategy.

---

# Chat API Philosophy

The chat system is:
- retrieval-grounded
- RBAC-protected
- tenant-aware
- citation-driven

LLM responses must never bypass:
- retrieval controls
- RBAC restrictions
- grounding validation

---

# Core Objectives

Chat APIs must:
- accept user questions
- orchestrate retrieval
- enforce RBAC
- generate grounded answers
- return citations
- expose hallucination scores

---

# Chat Workflow

The chat workflow includes:

1. Authentication
2. Tenant Resolution
3. Query Processing
4. Hybrid Retrieval
5. RBAC Filtering
6. Reranking
7. Prompt Assembly
8. LLM Generation
9. Hallucination Scoring
10. Citation Grounding
11. Streaming Response

---

# Recommended Endpoints

| Endpoint | Purpose |
|---|---|
| `/chat/query` | Standard chat query |
| `/chat/stream` | Streaming response |
| `/chat/history` | Conversation history |
| `/chat/feedback` | Feedback submission |
| `/chat/hallucination` | Hallucination metadata |

---

# Query Request Structure

Recommended fields:

```json
{
  "query": "string",
  "conversation_id": "string",
  "filters": {},
  "stream": true
}