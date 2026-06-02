from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import IdentityContext
from app.db.schema import audit_logs, conversations, messages, users


async def record_audit_event(
    *,
    session: AsyncSession,
    tenant_id: str,
    event_type: str,
    user_id: str | None = None,
    request_id: str = "system",
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    await session.execute(
        audit_logs.insert().values(
            id=str(uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            request_id=request_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
        )
    )


async def list_recent_activity(
    *, session: AsyncSession, identity: IdentityContext, limit: int = 25
) -> list[dict]:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can view activity.")
    rows = (
        await session.execute(
            select(
                audit_logs.c.id,
                audit_logs.c.event_type,
                audit_logs.c.resource_type,
                audit_logs.c.resource_id,
                audit_logs.c.metadata,
                audit_logs.c.created_at,
            )
            .where(audit_logs.c.tenant_id == identity.tenant.tenant_id)
            .order_by(audit_logs.c.created_at.desc())
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": row.id,
            "event_type": row.event_type,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "metadata": row.metadata or {},
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


async def list_query_audit_entries(
    *, session: AsyncSession, identity: IdentityContext, limit: int = 25
) -> list[dict]:
    assistant_messages = messages.alias("assistant_messages")
    user_messages = messages.alias("user_messages")
    query = (
        select(
            conversations.c.id.label("conversation_id"),
            conversations.c.created_at,
            users.c.email.label("user_email"),
            users.c.display_name.label("user_name"),
            user_messages.c.content.label("query"),
            assistant_messages.c.id.label("message_id"),
            assistant_messages.c.content.label("answer"),
            assistant_messages.c.citation_payload,
        )
        .select_from(
            conversations.join(
                assistant_messages,
                (assistant_messages.c.conversation_id == conversations.c.id)
                & (assistant_messages.c.tenant_id == conversations.c.tenant_id)
                & (assistant_messages.c.role == "assistant"),
            )
            .join(
                user_messages,
                (user_messages.c.conversation_id == conversations.c.id)
                & (user_messages.c.tenant_id == conversations.c.tenant_id)
                & (user_messages.c.role == "user"),
            )
            .outerjoin(
                users,
                (users.c.id == conversations.c.user_id)
                & (users.c.tenant_id == conversations.c.tenant_id),
            )
        )
        .where(conversations.c.tenant_id == identity.tenant.tenant_id)
    )
    if "tenant_admin" not in identity.roles:
        query = query.where(conversations.c.user_id == identity.user_id)
    rows = (
        await session.execute(
            query
            .order_by(conversations.c.created_at.desc())
            .limit(limit)
        )
    ).all()

    entries: list[dict] = []
    for row in rows:
        payload = row.citation_payload or {}
        entries.append(
            {
                "conversation_id": row.conversation_id,
                "message_id": row.message_id,
                "created_at": row.created_at.isoformat(),
                "user_email": row.user_email or "unknown",
                "user_name": row.user_name or "Unknown user",
                "query": row.query,
                "answer": row.answer,
                "retrieved_chunks": payload.get("retrieved_chunks", []),
                "citations": payload.get("citations", []),
                "hallucination": payload.get("hallucination", {}),
                "retrieval": payload.get("retrieval", {}),
            }
        )
    return entries
