from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import IdentityContext
from app.db.schema import audit_logs


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
