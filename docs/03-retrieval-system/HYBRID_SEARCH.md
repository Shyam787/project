# HYBRID_SEARCH

## Purpose

This document defines the authoritative hybrid search strategy for the platform.

It governs:
- dense retrieval
- sparse retrieval
- hybrid ranking
- score fusion
- retrieval balancing
- retrieval explainability

All retrieval implementation must comply with this strategy.

---

# Hybrid Search Philosophy

Enterprise retrieval cannot rely exclusively on:
- semantic vector similarity
or
- keyword matching

Each approach has strengths and weaknesses.

The platform combines both approaches to achieve:
- higher recall
- better precision
- improved enterprise relevance
- stronger grounding quality

---

# Why Hybrid Search Exists

Dense retrieval is strong at:
- semantic understanding
- paraphrase matching
- multilingual similarity

But weak at:
- exact keywords
- identifiers
- rare terms
- legal references

---

# Sparse Retrieval Strengths

BM25 is strong at:
- exact keyword matching
- identifiers
- policy references
- lexical recall

But weak at:
- semantic understanding
- paraphrases
- contextual similarity

---

# Hybrid Search Objective

The objective is to combine:
- semantic relevance
- lexical relevance

into one retrieval pipeline.

---

# Hybrid Search Architecture

The hybrid retrieval system contains:

1. Dense Retrieval Pipeline
2. Sparse Retrieval Pipeline
3. Score Fusion Layer
4. Candidate Aggregation Layer
5. RBAC Filtering
6. Reranking Layer

---

# Dense Retrieval

## Technology

Qdrant + BGE-M3 embeddings

---

## Responsibilities

Dense retrieval provides:
- semantic similarity
- multilingual semantic retrieval
- contextual relevance

---

## Workflow

1. query embedding generation
2. vector similarity search
3. top-n semantic candidate retrieval

---

## Constraints

Dense retrieval must:
- remain tenant-scoped
- preserve metadata
- expose similarity scores

---

# Sparse Retrieval

## Technology

BM25

---

## Responsibilities

Sparse retrieval provides:
- lexical relevance
- keyword matching
- exact phrase recall

---

## Workflow

1. query tokenization
2. BM25 scoring
3. top-n lexical candidate retrieval

---

## Constraints

Sparse retrieval must:
- remain tenant-aware
- preserve chunk traceability

---

# Fusion Layer

## Objective

Merge:
- dense ranking
- sparse ranking

into one unified ranking system.

---

# Selected Fusion Strategy

## Reciprocal Rank Fusion (RRF)

The platform uses:
- Reciprocal Rank Fusion

instead of raw score averaging.

---

# Why RRF Was Chosen

RRF improves:
- ranking robustness
- retrieval consistency
- score independence
- semantic-keyword balance

RRF avoids:
- unstable score normalization
- embedding-model-specific tuning

---

# RRF Formula

```text
RRF Score = Σ 1 / (k + rank)