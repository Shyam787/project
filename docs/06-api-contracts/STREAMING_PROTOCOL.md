# STREAMING_PROTOCOL

## Purpose

This document defines the authoritative streaming response protocol for the platform.

It governs:
- token streaming
- citation streaming
- generation event delivery
- frontend synchronization
- streaming observability
- streaming failure handling

All streaming implementation must comply with this strategy.

---

# Streaming Philosophy

Streaming exists to improve:
- perceived latency
- conversational responsiveness
- user experience
- operational transparency

Streaming must preserve:
- grounding integrity
- RBAC guarantees
- citation correctness

---

# Core Objectives

Streaming workflows must:
- progressively deliver responses
- preserve citation traceability
- expose generation state
- remain observable
- remain recoverable

---

# Streaming Architecture

The streaming workflow includes:

1. Query Submission
2. Retrieval Completion
3. Prompt Assembly
4. LLM Token Generation
5. Incremental Token Delivery
6. Citation Delivery
7. Completion Event

---

# Recommended Protocol

Recommended transport:
- Server-Sent Events (SSE)

Alternative future support:
- WebSockets

---

# Why SSE

SSE is preferred because:
- implementation simplicity
- frontend compatibility
- stable token delivery
- lower operational complexity

---

# Streaming Event Types

Recommended event types:

| Event | Purpose |
|---|---|
| `message_start` | Response started |
| `token` | Token chunk |
| `citation` | Citation metadata |
| `hallucination` | Hallucination metadata |
| `message_end` | Stream completed |
| `error` | Stream failure |

---

# Recommended Event Structure

```json
{
  "event": "token",
  "data": {
    "content": "partial text"
  }
}