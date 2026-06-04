# Enterprise RAG Platform

A production-oriented, multi-tenant Retrieval-Augmented Generation platform for private enterprise documents. The system combines identity management, tenant isolation, document-level RBAC, hybrid retrieval, cross-encoder reranking, grounded answer generation, hallucination risk scoring, feedback capture, auditability, and observability.

## What The System Does

Enterprise RAG Platform allows an organization to upload internal documents, assign role-based access, and ask questions against only the information that the signed-in user is authorized to see.

The retrieval pipeline is security-first:

```text
Authentication
-> Tenant resolution
-> RBAC filtering
-> Dense retrieval
-> BM25 sparse retrieval
-> Reciprocal Rank Fusion
-> Cross-encoder reranking
-> Context assembly
-> Grounded answer generation
-> Citations, hallucination scoring, audit logging, feedback
```

Unauthorized documents are filtered before vector search, BM25 search, reranking, prompt construction, citation generation, and hallucination scoring.

## Core Capabilities

- Multi-tenant organization onboarding
- Keycloak-backed authentication and role claims
- Tenant-isolated document namespaces
- Admin-managed organization users and roles
- Document upload, metadata, access assignment, archive, restore, soft delete, and hard delete
- PDF, DOCX, TXT, and Markdown text extraction
- Chunking and embedding pipeline
- Qdrant dense vector search
- `rank_bm25` sparse retrieval
- Reciprocal Rank Fusion for hybrid result merging
- Local cross-encoder reranking with `cross-encoder/ms-marco-MiniLM-L-6-v2`
- BGE-M3 embeddings with `BAAI/bge-m3`
- Groq-backed answer generation with safe grounded fallback behavior
- Citations linked to source documents
- Hallucination risk scoring against retrieved context
- Thumbs-up/thumbs-down feedback capture with retrieval traces
- Audit log viewer for queries, retrieved sources, answers, feedback, and governance events
- Prometheus metrics and Grafana dashboards
- Docker Compose local runtime
- Kubernetes and Terraform deployment artifacts for cloud readiness

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, SQLAlchemy Core |
| Identity | Keycloak |
| Metadata database | PostgreSQL |
| Vector database | Qdrant |
| Sparse retrieval | `rank_bm25` |
| Embeddings | `sentence-transformers`, `BAAI/bge-m3` |
| Reranking | `sentence-transformers` CrossEncoder, `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM provider | Groq API |
| Cache | Redis |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Local runtime | Docker Compose |
| Cloud artifacts | Kubernetes manifests, Terraform scaffold |

## Application URLs

After the stack is running:

| Service | URL |
| --- | --- |
| Web application | http://localhost:3002 |
| Backend API | http://localhost:8000 |
| Backend readiness | http://localhost:8000/ready |
| Keycloak | http://localhost:8081 |
| Qdrant dashboard | http://localhost:6333/dashboard |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

## Local Setup

### 1. Configure Environment

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Update the required values in `.env`, especially:

```text
POSTGRES_PASSWORD
KEYCLOAK_ADMIN_PASSWORD
GRAFANA_ADMIN_PASSWORD
GROQ_API_KEY
```

### 2. Start The Platform

```powershell
docker compose --env-file .env up -d --build
```

### 3. Verify Runtime Health

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/ready
```

Expected pipeline order:

```text
auth, tenant_resolve, rbac, retrieval, rrf, rerank, context, llm
```

## First-Time Use

1. Open the web application at http://localhost:3002.
2. Create an organization from the organization onboarding page.
3. Sign in with the administrator account created during onboarding.
4. Open the Users section and create organization users with appropriate roles.
5. Upload documents from the Documents section.
6. Assign document access by role.
7. Ask questions from the Ask section.
8. Review citations, grounding quality, hallucination risk, and retrieved source files.
9. Submit feedback on generated answers.
10. Review audit logs and observability dashboards.

## Roles

The platform supports organization-scoped roles:

- `tenant_admin`
- `manager`
- `employee`
- `hr`
- `finance`
- `security`

Only tenant administrators manage users, documents, access assignments, and organization settings. Other users retrieve answers only from documents allowed for their assigned role.

## Document Governance

Documents are stored with tenant-scoped metadata and access controls. Document lifecycle actions include:

- upload
- view metadata
- download
- archive
- restore from archive
- soft delete
- restore from soft delete
- hard delete with confirmation

Document access is enforced at retrieval time. A user cannot retrieve, rerank, cite, or generate from content outside their tenant or role permissions.

## Retrieval And Answering

The query system uses both semantic and lexical retrieval:

1. The backend validates the Keycloak JWT.
2. The tenant and user roles are resolved.
3. Authorized document/chunk scope is calculated.
4. Qdrant performs dense vector search over authorized chunks.
5. BM25 performs sparse keyword search over authorized chunks.
6. Reciprocal Rank Fusion merges dense and sparse candidates.
7. A cross-encoder reranks the top fused candidates.
8. The final context is assembled with citations.
9. The LLM generates an answer only from authorized context.
10. The response is scored for hallucination risk.

If no authorized evidence exists, the system returns a safe fallback instead of inventing an answer.

## Feedback And Auditability

Every answer can receive thumbs-up or thumbs-down feedback. Feedback is stored with:

- tenant
- user
- answer message
- rating
- retrieval trace
- timestamp

This supports retrieval-quality analysis, trend review, and future tuning decisions without silently changing ranking behavior in a way that would weaken auditability.

Audit logs record governed events such as:

- organization creation
- user creation and updates
- document lifecycle actions
- queries
- retrieved source references
- generated responses
- feedback submissions

Administrators can review organization-wide audit records. Regular users see only their own query audit history.

## Observability

Prometheus collects platform metrics, including:

- API request rates
- RBAC denials
- tenant isolation violation attempts
- retrieval, reranking, and generation latency
- hallucination score distribution
- retrieval quality gauges by tenant, document set, and metric

Grafana provides operational dashboards for request flow, latency, security events, and hallucination trends.

Prometheus alert rules include:

- high API error rate
- RBAC denial spike
- tenant isolation violation attempt
- hallucination score spike above threshold

Chat answer generation is protected by a Redis-backed per-user rate limit. The default limit is 20 answer requests per user per hour and can be changed with:

```text
CHAT_RATE_LIMIT_REQUESTS=20
CHAT_RATE_LIMIT_WINDOW_SECONDS=3600
```

## Database Access

PostgreSQL is exposed for local GUI tools on port `55432`.

Use the following DBeaver settings:

```text
Host: localhost
Port: 55432
Database: enterprise_rag
Username: enterprise_rag
Password: value from .env POSTGRES_PASSWORD
```

Inside Docker, services still communicate with PostgreSQL through the container network on `postgres:5432`. The `55432` port is only the host-facing port for local tools.

## Validation

Backend tests:

```powershell
python -m pytest backend\tests -q
```

Frontend typecheck:

```powershell
cd frontend
npx.cmd tsc --noEmit
```

Docker runtime check:

```powershell
docker compose --env-file .env ps
Invoke-WebRequest -UseBasicParsing http://localhost:8000/ready
```

## Deployment Notes

Docker Compose is the supported local runtime.

Kubernetes manifests and Terraform files are included as cloud-readiness artifacts. They define the expected production shape: isolated namespaces, network policies, service boundaries, persistent infrastructure, and infrastructure-as-code ownership.

These cloud artifacts are not automatically applied during local setup because running cloud Kubernetes clusters, managed databases, public load balancers, storage volumes, TLS, and monitoring infrastructure can create unnecessary cost. Apply them only when deploying to a funded cloud environment with production secrets, TLS, backups, and region-specific compliance controls configured.

For DPDP-aware deployment, production data residency must be configured so PostgreSQL, Qdrant, Redis, Keycloak storage, document volumes, logs, and backups remain in approved Indian cloud regions. The local Docker runtime keeps data on the host machine; regional residency is a production deployment control rather than a local development behavior.

## Security Notes

- Keep `.env` out of source control.
- Rotate any shared local credentials before real deployment.
- Use HTTPS and managed secrets in production.
- Restrict database, Redis, and Qdrant exposure outside the cluster.
- Keep tenant isolation and RBAC filtering before retrieval.
- Review audit logs and observability alerts regularly.
