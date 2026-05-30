# Enterprise RAG

Document-driven, multi-tenant Enterprise RAG system with compliance, RBAC, hybrid retrieval, citations, hallucination visibility, auditability, and observability.

The implementation is governed by `docs/`. Build phases must follow `docs/12-implementation-roadmap/IMPLEMENTATION_PHASES.md`.

## Local Bootstrap

1. Copy `.env.example` to `.env` and replace placeholder values.
2. Start the local stack:

```powershell
docker compose up --build
```

3. Backend health endpoint:

```text
http://localhost:8000/health
```

Phase 0 exposes only operational endpoints. Protected enterprise workflows are added in later governed phases.
