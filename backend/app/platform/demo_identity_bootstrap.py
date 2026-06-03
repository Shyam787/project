import asyncio
from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schema import roles, user_roles, users
from app.platform.keycloak_admin import KeycloakAdminClient


@dataclass(frozen=True)
class DemoIdentity:
    email: str
    full_name: str
    role: str
    password: str


DEMO_IDENTITIES = (
    DemoIdentity("admin@synycs.com", "Synycs Admin", "tenant_admin", "DemoAdmin123!"),
    DemoIdentity("manager@synycs.com", "Synycs Manager", "manager", "DemoManager123!"),
    DemoIdentity("employee@synycs.com", "Synycs Employee", "employee", "DemoEmployee123!"),
    DemoIdentity("shyam@synycs.com", "Shyam HR", "hr", "DemoHr123!"),
    DemoIdentity("malli@synycs.com", "Malli Finance", "finance", "DemoFinance123!"),
    DemoIdentity("esh@synycs.com", "Esh Security", "security", "DemoSecurity123!"),
)


async def ensure_demo_keycloak_identities(
    *, session: AsyncSession, keycloak: KeycloakAdminClient, tenant_id: str = "synycs"
) -> None:
    for identity in DEMO_IDENTITIES:
        user_row = (
            await session.execute(
                select(users.c.id, users.c.external_subject).where(
                    users.c.tenant_id == tenant_id,
                    users.c.email == identity.email,
                )
            )
        ).first()
        if user_row is None:
            continue
        role_row = (
            await session.execute(
                select(roles.c.id).where(
                    roles.c.tenant_id == tenant_id,
                    roles.c.name == identity.role,
                )
            )
        ).first()
        if role_row is None:
            continue

        keycloak_id = await _upsert_keycloak_identity(
            keycloak=keycloak,
            identity=identity,
            tenant_id=tenant_id,
            local_user_id=user_row.id,
            current_external_subject=user_row.external_subject,
        )
        await session.execute(
            update(users)
            .where(users.c.id == user_row.id, users.c.tenant_id == tenant_id)
            .values(
                external_subject=keycloak_id,
                display_name=identity.full_name,
                is_active=True,
            )
        )
        await session.execute(
            user_roles.delete().where(
                user_roles.c.user_id == user_row.id,
                user_roles.c.tenant_id == tenant_id,
            )
        )
        await session.execute(
            user_roles.insert().values(
                id=f"demo-role-{tenant_id}-{identity.role}-{identity.email}",
                tenant_id=tenant_id,
                user_id=user_row.id,
                role_id=role_row.id,
            )
        )


async def ensure_demo_keycloak_identities_with_retry(
    *, session: AsyncSession, keycloak: KeycloakAdminClient, attempts: int = 8
) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            await ensure_demo_keycloak_identities(session=session, keycloak=keycloak)
            return
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(min(2**attempt, 8))
    if last_error is not None:
        raise last_error


async def _upsert_keycloak_identity(
    *,
    keycloak: KeycloakAdminClient,
    identity: DemoIdentity,
    tenant_id: str,
    local_user_id: str,
    current_external_subject: str,
) -> str:
    try:
        return await keycloak.update_user(
            user_id=current_external_subject,
            full_name=identity.full_name,
            tenant_id=tenant_id,
            roles={identity.role},
            enabled=True,
            password=identity.password,
            lookup_values=[identity.email, local_user_id],
        )
    except Exception:
        created = await keycloak.create_user(
            email=identity.email,
            full_name=identity.full_name,
            tenant_id=tenant_id,
            roles={identity.role},
            password=identity.password,
            temporary=False,
            enabled=True,
        )
        return created["keycloak_id"]
