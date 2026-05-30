# ALERTING_RULES

## Purpose

This document defines the authoritative alerting strategy for the platform.

It governs:
- system alerts
- performance alerts
- security alerts
- retrieval alerts
- hallucination alerts
- infrastructure alerts

All alerting implementation must comply with this strategy.

---

# Alerting Philosophy

Alerting must be:
- actionable
- minimal noise
- high signal
- role-aware
- tenant-aware

False positives are harmful and must be minimized.

---

# Core Objectives

Alerts must:
- detect system failures
- detect performance degradation
- detect security violations
- detect retrieval quality drop
- detect hallucination spikes

---

# Alert Categories

The system supports:

1. System Health Alerts
2. Performance Alerts
3. Security Alerts
4. Retrieval Quality Alerts
5. Hallucination Alerts
6. Infrastructure Alerts

---

# System Health Alerts

Trigger on:
- service downtime
- API failure spikes
- container crashes

---

# Performance Alerts

Trigger on:
- high API latency
- retrieval slowdown
- reranking delays
- LLM latency spikes

---

# Security Alerts

Trigger on:
- RBAC violations
- unauthorized access attempts
- tenant isolation breaches

---

# Retrieval Quality Alerts

Trigger on:
- drop in precision@k
- drop in recall@k
- MRR degradation
- indexing failures

---

# Hallucination Alerts

Trigger on:
- hallucination score > threshold
- sudden spike in hallucinations
- grounding failures

Recommended threshold:
```text
> 0.15 average hallucination score