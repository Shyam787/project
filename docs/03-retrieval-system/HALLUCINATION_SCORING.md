# HALLUCINATION_SCORING

## Purpose

This document defines the authoritative hallucination scoring strategy for the platform.

It governs:
- grounding validation
- unsupported claim detection
- hallucination scoring
- confidence classification
- hallucination observability

All hallucination analysis implementation must comply with this strategy.

---

# Hallucination Philosophy

Enterprise RAG systems must not blindly trust generated output.

The system must:
- validate grounding
- measure evidence support
- identify unsupported claims
- expose hallucination confidence

Hallucination detection is mandatory.

---

# Core Objective

Every generated response must be evaluated against:
- retrieved chunks
- grounded evidence
- citation mappings

The platform must estimate:
- how much of the response is supported
- which claims are unsupported
- grounding confidence levels

---

# Hallucination Definition

A hallucination occurs when:
- the generated response contains unsupported claims
- retrieved evidence does not support generated content
- citations do not align with claims

---

# Hallucination Categories

The system classifies hallucinations into:

1. Unsupported Claim
2. Incorrect Attribution
3. Fabricated Information
4. Partial Grounding
5. Citation Drift

---

# Hallucination Pipeline

The hallucination pipeline contains:

1. Response Parsing
2. Claim Extraction
3. Evidence Mapping
4. Claim-Evidence Comparison
5. Grounding Evaluation
6. Hallucination Scoring
7. Confidence Classification

---

# Response Parsing

## Responsibilities

The system parses:
- generated response text
- citations
- chunk references

---

# Claim Extraction

## Responsibilities

The system extracts:
- factual claims
- referenced assertions
- grounded statements

---

# Evidence Mapping

## Responsibilities

The system maps:
- claims to retrieved chunks
- citations to source evidence
- claims to supporting context

---

# Claim-Evidence Comparison

## Responsibilities

The system evaluates:
- semantic alignment
- evidence sufficiency
- factual support

---

# Grounding Evaluation

## Responsibilities

The system determines:
- fully supported claims
- partially supported claims
- unsupported claims

---

# Hallucination Score

## Objective

The hallucination score estimates:
- grounding confidence
- unsupported content ratio

---

# Score Range

Recommended scale:

```text
0.0 → Fully grounded
1.0 → Completely unsupported