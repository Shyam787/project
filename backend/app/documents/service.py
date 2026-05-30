from uuid import uuid4
from io import BytesIO
from pathlib import Path
import re
from datetime import datetime, timezone

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from docx import Document
from pypdf import PdfReader

from app.auth.models import IdentityContext
from app.core.config import Settings
from app.db.schema import chunks, document_permissions, documents, roles, tenants, users
from app.retrieval.chunking import build_chunks
from app.retrieval.models import ChunkRecord
from app.retrieval.qdrant_store import QdrantVectorStore

SUPPORTED_TEXT_TYPES = {
    "text/plain",
    "text/markdown",
    "application/octet-stream",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
CLASSIFICATIONS = {"Public", "Internal", "Confidential", "Restricted"}
ACTIVE_STATUSES = {"completed", "processing", "pending", "failed"}


async def ensure_identity_records(
    *,
    session: AsyncSession,
    identity: IdentityContext,
    extra_roles: set[str] | None = None,
) -> None:
    tenant_id = identity.tenant.tenant_id
    user_id = identity.user_id
    await session.execute(
        insert(tenants)
        .values(id=tenant_id, name=tenant_id, slug=tenant_id)
        .on_conflict_do_nothing(index_elements=["id"])
    )
    await session.execute(
        insert(users)
        .values(
            id=user_id,
            tenant_id=tenant_id,
            external_subject=user_id,
            email=f"{user_id}@local.invalid",
            display_name=user_id,
        )
        .on_conflict_do_nothing(index_elements=["id"])
    )
    for role in identity.roles | (extra_roles or set()):
        await session.execute(
            insert(roles)
            .values(
                id=str(uuid4()),
                tenant_id=tenant_id,
                name=role,
                description=f"{role} role",
            )
            .on_conflict_do_nothing(constraint="uq_roles_tenant_name")
        )


async def upload_text_document(
    *,
    session: AsyncSession,
    vector_store: QdrantVectorStore,
    identity: IdentityContext,
    filename: str,
    content_type: str,
    raw_bytes: bytes,
    allowed_roles: set[str],
    pii_sensitive: bool,
    classification: str,
    settings: Settings,
) -> dict:
    if content_type not in SUPPORTED_TEXT_TYPES and not filename.endswith((".txt", ".md", ".pdf", ".docx")):
        raise ValueError("Only PDF, DOCX, TXT, and Markdown uploads are currently supported.")
    text = extract_document_text(
        filename=filename,
        content_type=content_type,
        raw_bytes=raw_bytes,
    )
    if not text.strip():
        raise ValueError("Uploaded document is empty.")
    if classification not in CLASSIFICATIONS:
        raise ValueError("Unsupported document classification.")

    await ensure_identity_records(
        session=session,
        identity=identity,
        extra_roles=allowed_roles,
    )
    document_id = str(uuid4())
    stored_path = store_uploaded_file(
        storage_root=settings.storage_root,
        tenant_id=identity.tenant.tenant_id,
        document_id=document_id,
        filename=filename,
        raw_bytes=raw_bytes,
    )
    await session.execute(
        insert(documents).values(
            id=document_id,
            tenant_id=identity.tenant.tenant_id,
            owner_id=identity.user_id,
            title=filename,
            document_type=content_type or "text/plain",
            storage_uri=str(stored_path),
            ingestion_status="processing",
            pii_sensitive=pii_sensitive,
            metadata={
                "filename": filename,
                "allowed_roles": sorted(allowed_roles),
                "classification": classification,
                "uploaded_by": identity.user_id,
                "storage_path": str(stored_path),
                "state": "Active",
                "query_count": 0,
            },
        )
    )

    role_rows = (
        await session.execute(
            select(roles.c.id, roles.c.name).where(
                roles.c.tenant_id == identity.tenant.tenant_id,
                roles.c.name.in_(allowed_roles),
            )
        )
    ).all()
    for role_id, _role_name in role_rows:
        await session.execute(
            insert(document_permissions).values(
                id=str(uuid4()),
                tenant_id=identity.tenant.tenant_id,
                document_id=document_id,
                role_id=role_id,
                permission="document_read",
            )
        )

    chunk_records = build_chunks(
        tenant_id=identity.tenant.tenant_id,
        document_id=document_id,
        text=text,
        metadata={"source_location": {"filename": filename}},
        target_tokens=450,
    )
    for chunk in chunk_records:
        await session.execute(
            insert(chunks).values(
                id=chunk.chunk_id,
                tenant_id=chunk.tenant_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.chunk_text,
                token_count=len(chunk.chunk_text.split()),
                metadata=chunk.metadata,
            )
        )
    await vector_store.upsert_chunks(tenant_id=identity.tenant.tenant_id, chunks=chunk_records)
    await session.execute(
        documents.update()
        .where(documents.c.id == document_id)
        .values(ingestion_status="completed")
    )
    return {
        "document_id": document_id,
        "title": filename,
        "status": "completed",
        "chunk_count": len(chunk_records),
        "allowed_roles": sorted(allowed_roles),
        "classification": classification,
        "storage_path": str(stored_path),
    }


async def list_documents_for_identity(
    *, session: AsyncSession, identity: IdentityContext
) -> list[dict]:
    from_clause = documents.outerjoin(
        chunks,
        (chunks.c.document_id == documents.c.id)
        & (chunks.c.tenant_id == documents.c.tenant_id),
    )
    base = select(
        documents.c.id,
        documents.c.title,
        documents.c.ingestion_status,
        documents.c.pii_sensitive,
        documents.c.created_at,
        documents.c.updated_at,
        documents.c.owner_id,
        documents.c.metadata,
        func.count(chunks.c.id).label("chunk_count"),
    )
    if "tenant_admin" not in identity.roles:
        role_names = list(identity.roles)
        from_clause = (
            from_clause.join(
                document_permissions,
                (document_permissions.c.document_id == documents.c.id)
                & (document_permissions.c.tenant_id == documents.c.tenant_id),
            ).join(roles, roles.c.id == document_permissions.c.role_id)
        )
        base = base.where(roles.c.name.in_(role_names))
    base = base.select_from(from_clause).where(documents.c.tenant_id == identity.tenant.tenant_id)
    rows = (
        await session.execute(
            base.group_by(
                documents.c.id,
                documents.c.title,
                documents.c.ingestion_status,
                documents.c.pii_sensitive,
                documents.c.created_at,
                documents.c.updated_at,
                documents.c.owner_id,
                documents.c.metadata,
            ).order_by(documents.c.created_at.desc())
        )
    ).all()
    return [
        {
            "document_id": row.id,
            "title": row.title,
            "status": row.ingestion_status,
            "state": (row.metadata or {}).get("state", status_to_state(row.ingestion_status)),
            "pii_sensitive": row.pii_sensitive,
            "uploaded_by": (row.metadata or {}).get("uploaded_by", row.owner_id),
            "classification": (row.metadata or {}).get("classification", "Internal"),
            "allowed_roles": (row.metadata or {}).get("allowed_roles", []),
            "chunk_count": int(row.chunk_count or 0),
            "storage_path": (row.metadata or {}).get("storage_path", ""),
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
        for row in rows
    ]


async def repository_summary(*, session: AsyncSession, identity: IdentityContext) -> dict:
    docs = await list_documents_for_identity(session=session, identity=identity)
    return {
        "total_documents": len(docs),
        "indexed_documents": sum(1 for doc in docs if doc["status"] == "completed"),
        "indexed_chunks": sum(int(doc["chunk_count"]) for doc in docs),
        "classifications": {
            name: sum(1 for doc in docs if doc["classification"] == name)
            for name in sorted(CLASSIFICATIONS)
        },
        "recent_uploads": docs[:5],
    }


async def get_document_for_identity(
    *, session: AsyncSession, identity: IdentityContext, document_id: str
) -> dict | None:
    docs = await list_documents_for_identity(session=session, identity=identity)
    return next((doc for doc in docs if doc["document_id"] == document_id), None)


async def archive_document(
    *, session: AsyncSession, identity: IdentityContext, document_id: str
) -> dict:
    doc = await require_manageable_document(
        session=session, identity=identity, document_id=document_id
    )
    metadata = dict(doc["metadata"] or {})
    metadata["state"] = "Archived"
    metadata["archive_date"] = datetime.now(timezone.utc).isoformat()
    await session.execute(
        update(documents)
        .where(documents.c.id == document_id)
        .where(documents.c.tenant_id == identity.tenant.tenant_id)
        .values(ingestion_status="archived", metadata=metadata)
    )
    return {"document_id": document_id, "state": "Archived"}


async def restore_document(
    *, session: AsyncSession, identity: IdentityContext, document_id: str
) -> dict:
    doc = await require_manageable_document(
        session=session, identity=identity, document_id=document_id
    )
    metadata = dict(doc["metadata"] or {})
    metadata["state"] = "Active"
    metadata.pop("archive_date", None)
    await session.execute(
        update(documents)
        .where(documents.c.id == document_id)
        .where(documents.c.tenant_id == identity.tenant.tenant_id)
        .values(ingestion_status="completed", metadata=metadata)
    )
    return {"document_id": document_id, "state": "Active"}


async def soft_delete_document(
    *, session: AsyncSession, identity: IdentityContext, document_id: str
) -> dict:
    doc = await require_manageable_document(
        session=session, identity=identity, document_id=document_id
    )
    metadata = dict(doc["metadata"] or {})
    metadata["state"] = "Deleted"
    metadata["deletion_date"] = datetime.now(timezone.utc).isoformat()
    await session.execute(
        update(documents)
        .where(documents.c.id == document_id)
        .where(documents.c.tenant_id == identity.tenant.tenant_id)
        .values(ingestion_status="soft_deleted", metadata=metadata)
    )
    return {"document_id": document_id, "state": "Deleted"}


async def permanently_delete_document(
    *,
    session: AsyncSession,
    vector_store: QdrantVectorStore,
    identity: IdentityContext,
    document_id: str,
) -> dict:
    doc = await require_manageable_document(
        session=session, identity=identity, document_id=document_id
    )
    storage_path = (doc["metadata"] or {}).get("storage_path") or doc["storage_uri"]
    await vector_store.delete_document(
        tenant_id=identity.tenant.tenant_id, document_id=document_id
    )
    await session.execute(
        delete(chunks)
        .where(chunks.c.document_id == document_id)
        .where(chunks.c.tenant_id == identity.tenant.tenant_id)
    )
    await session.execute(
        delete(document_permissions)
        .where(document_permissions.c.document_id == document_id)
        .where(document_permissions.c.tenant_id == identity.tenant.tenant_id)
    )
    await session.execute(
        delete(documents)
        .where(documents.c.id == document_id)
        .where(documents.c.tenant_id == identity.tenant.tenant_id)
    )
    if storage_path:
        Path(storage_path).unlink(missing_ok=True)
    return {"document_id": document_id, "state": "Permanently Deleted", "deleted": True}


async def require_manageable_document(
    *, session: AsyncSession, identity: IdentityContext, document_id: str
):
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can manage document lifecycle.")
    row = (
        await session.execute(
            select(
                documents.c.id,
                documents.c.storage_uri,
                documents.c.metadata,
            ).where(
                documents.c.id == document_id,
                documents.c.tenant_id == identity.tenant.tenant_id,
            )
        )
    ).mappings().first()
    if row is None:
        raise ValueError("Document not found.")
    return row


def store_uploaded_file(
    *, storage_root: str, tenant_id: str, document_id: str, filename: str, raw_bytes: bytes
) -> Path:
    safe_name = sanitize_filename(filename)
    tenant_dir = Path(storage_root) / tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    path = tenant_dir / f"{document_id}-{safe_name}"
    path.write_bytes(raw_bytes)
    return path


def sanitize_filename(filename: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._") or "document.txt"


def status_to_state(status: str) -> str:
    return {
        "archived": "Archived",
        "soft_deleted": "Deleted",
        "completed": "Active",
        "processing": "Processing",
        "pending": "Pending",
        "failed": "Failed",
    }.get(status, status)


def extract_document_text(
    *,
    filename: str,
    content_type: str,
    raw_bytes: bytes,
) -> str:
    lowered = filename.lower()
    if content_type == "application/pdf" or lowered.endswith(".pdf"):
        reader = PdfReader(BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or lowered.endswith(".docx")
    ):
        document = Document(BytesIO(raw_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    return raw_bytes.decode("utf-8")


async def authorized_chunks_for_identity(
    *, session: AsyncSession, identity: IdentityContext
) -> list[ChunkRecord]:
    role_names = list(identity.roles)
    query = (
        select(
            chunks.c.id,
            chunks.c.document_id,
            chunks.c.tenant_id,
            chunks.c.content,
            chunks.c.chunk_index,
            chunks.c.metadata,
        )
        .select_from(
            chunks.join(
                documents,
                (documents.c.id == chunks.c.document_id)
                & (documents.c.tenant_id == chunks.c.tenant_id),
            ).join(
                document_permissions,
                (document_permissions.c.document_id == chunks.c.document_id)
                & (document_permissions.c.tenant_id == chunks.c.tenant_id),
            ).join(roles, roles.c.id == document_permissions.c.role_id)
        )
        .where(chunks.c.tenant_id == identity.tenant.tenant_id)
        .where(roles.c.name.in_(role_names))
        .where(document_permissions.c.permission == "document_read")
        .where(documents.c.ingestion_status == "completed")
    )
    rows = (await session.execute(query)).all()
    return [
        ChunkRecord(
            chunk_id=row.id,
            document_id=row.document_id,
            tenant_id=row.tenant_id,
            chunk_text=row.content,
            chunk_index=row.chunk_index,
            metadata=row.metadata or {},
        )
        for row in rows
    ]
