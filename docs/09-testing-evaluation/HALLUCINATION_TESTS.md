# HALLUCINATION_TESTS

## Purpose

This document defines hallucination detection and evaluation test cases for the platform.

It ensures:
- LLM outputs are grounded in retrieved context
- unsupported claims are detected
- citation accuracy is enforced
- hallucination scoring is reliable

---

# Hallucination Philosophy

The system must ensure:
- no ungrounded statements
- no fabricated citations
- no unsupported facts

Every response must be traceable to retrieved chunks.

---

# Core Objectives

Tests must validate:
- factual grounding
- citation correctness
- response consistency with retrieval context
- hallucination score accuracy

---

# Hallucination Definition

A hallucination occurs when:
- response contains facts not present in retrieved context
- response fabricates entities, numbers, or claims
- response misrepresents source content

---

# Test Categories

1. Grounded Response Tests
2. Ungrounded Claim Detection Tests
3. Citation Accuracy Tests
4. Retrieval Mismatch Tests
5. Adversarial Hallucination Tests

---

# Grounded Response Tests

Ensure:
- every claim maps to retrieved chunks
- all facts are supported by context
- no external knowledge leakage occurs

---

# Ungrounded Claim Detection Tests

Ensure detection of:
- fabricated numbers
- invented entities
- false relationships
- unsupported conclusions

---

# Citation Accuracy Tests

Ensure:
- each citation points to correct chunk
- citation text matches source
- no citation duplication errors

---

# Retrieval Mismatch Tests

Ensure:
- response does not use non-retrieved data
- irrelevant retrieved chunks are ignored
- correct chunk selection is used

---

# Adversarial Hallucination Tests

Include prompts like:
- misleading questions
- incomplete context queries
- cross-tenant trick prompts
- prompt injection attempts

---

# Hallucination Scoring System Tests

Validate:
- hallucination score consistency
- scoring sensitivity
- threshold correctness

Recommended threshold:
```text
> 0.15 = potential hallucination risk