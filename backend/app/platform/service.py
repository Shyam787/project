import re
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import record_audit_event
from app.auth.models import IdentityContext
from app.db.schema import roles, tenants, user_roles, users
from app.platform.keycloak_admin import KeycloakAdminClient

DEFAULT_ROLES = {"tenant_admin", "manager", "employee", "viewer"}
ORG_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


def validate_password(password: str) -> None:
    checks = [
        (len(password) >= 12, "Password must contain at least 12 characters."),
        (any(char.isupper() for char in password), "Password must contain an uppercase letter."),
        (any(char.islower() for char in password), "Password must contain a lowercase letter."),
        (any(char.isdigit() for char in password), "Password must contain a number."),
        (any(not char.isalnum() for char in password), "Password must contain a special character."),
    ]
    for passed, message in checks:
        if not passed:
            raise ValueError(message)


def validate_org(name: str, org_id: str, password: str, confirm_password: str) -> None:
    if len(name.strip()) < 3 or len(name.strip()) > 100:
        raise ValueError("Organization name must be between 3 and 100 characters.")
    if not ORG_ID_PATTERN.match(org_id):
        raise ValueError("Organization ID may contain only lowercase letters, numbers, and hyphens.")
    if password != confirm_password:
        raise ValueError("Password and confirmation do not match.")
    validate_password(password)


async def create_organization(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    organization_name: str,
    organization_id: str,
    admin_full_name: str,
    admin_email: str,
    password: str,
    confirm_password: str,
    request_id: str,
) -> dict:
    validate_org(organization_name, organization_id, password, confirm_password)
    exists = (
        await session.execute(select(tenants.c.id).where(tenants.c.id == organization_id))
    ).first()
    if exists:
        raise ValueError("Organization ID already exists.")

    await session.execute(
        insert(tenants).values(
            id=organization_id,
            name=organization_name.strip(),
            slug=organization_id,
        )
    )
    role_ids: dict[str, str] = {}
    for role_name in sorted(DEFAULT_ROLES):
        role_id = str(uuid4())
        role_ids[role_name] = role_id
        await session.execute(
            insert(roles).values(
                id=role_id,
                tenant_id=organization_id,
                name=role_name,
                description=f"{role_name} role",
            )
        )
    keycloak_user = await keycloak.create_user(
        email=admin_email,
        full_name=admin_full_name,
        tenant_id=organization_id,
        roles={"tenant_admin"},
        password=password,
        temporary=False,
    )
    await session.execute(
        insert(users).values(
            id=keycloak_user["keycloak_id"],
            tenant_id=organization_id,
            external_subject=keycloak_user["keycloak_id"],
            email=admin_email,
            display_name=admin_full_name,
        )
    )
    await session.execute(
        insert(user_roles).values(
            id=str(uuid4()),
            tenant_id=organization_id,
            user_id=keycloak_user["keycloak_id"],
            role_id=role_ids["tenant_admin"],
        )
    )
    await record_audit_event(
        session=session,
        tenant_id=organization_id,
        user_id=keycloak_user["keycloak_id"],
        request_id=request_id,
        event_type="Organization Created",
        resource_type="organization",
        resource_id=organization_id,
        metadata={"organization_name": organization_name, "admin_email": admin_email},
    )
    return {
        "organization_id": organization_id,
        "organization_name": organization_name,
        "admin_email": admin_email,
        "roles": sorted(DEFAULT_ROLES),
    }


async def list_users(*, session: AsyncSession, identity: IdentityContext) -> list[dict]:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can view users.")
    rows = (
        await session.execute(
            select(
                users.c.id,
                users.c.email,
                users.c.display_name,
                users.c.is_active,
                roles.c.name.label("role_name"),
                users.c.created_at,
            )
            .select_from(
                users.outerjoin(user_roles, user_roles.c.user_id == users.c.id).outerjoin(
                    roles, roles.c.id == user_roles.c.role_id
                )
            )
            .where(users.c.tenant_id == identity.tenant.tenant_id)
            .order_by(users.c.created_at.desc())
        )
    ).all()
    grouped: dict[str, dict] = {}
    for row in rows:
        item = grouped.setdefault(
            row.id,
            {
                "user_id": row.id,
                "email": row.email,
                "full_name": row.display_name,
                "is_active": row.is_active,
                "roles": [],
                "created_at": row.created_at.isoformat(),
            },
        )
        if row.role_name:
            item["roles"].append(row.role_name)
    return list(grouped.values())


async def create_tenant_user(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    identity: IdentityContext,
    full_name: str,
    email: str,
    role: str,
    request_id: str,
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can create users.")
    if role not in DEFAULT_ROLES:
        raise ValueError("Unsupported role.")
    role_row = (
        await session.execute(
            select(roles.c.id).where(
                roles.c.tenant_id == identity.tenant.tenant_id,
                roles.c.name == role,
            )
        )
    ).first()
    if role_row is None:
        raise ValueError("Role is not configured for this tenant.")
    keycloak_user = await keycloak.create_user(
        email=email,
        full_name=full_name,
        tenant_id=identity.tenant.tenant_id,
        roles={role},
        temporary=False,
    )
    await session.execute(
        insert(users)
        .values(
            id=keycloak_user["keycloak_id"],
            tenant_id=identity.tenant.tenant_id,
            external_subject=keycloak_user["keycloak_id"],
            email=email,
            display_name=full_name,
        )
        .on_conflict_do_nothing(index_elements=["id"])
    )
    await session.execute(
        insert(user_roles)
        .values(
            id=str(uuid4()),
            tenant_id=identity.tenant.tenant_id,
            user_id=keycloak_user["keycloak_id"],
            role_id=role_row.id,
        )
        .on_conflict_do_nothing(constraint="uq_user_roles_scope")
    )
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=identity.user_id,
        request_id=request_id,
        event_type="User Created",
        resource_type="user",
        resource_id=keycloak_user["keycloak_id"],
        metadata={"email": email, "role": role},
    )
    return {
        "user_id": keycloak_user["keycloak_id"],
        "email": email,
        "role": role,
        "temporary_password": keycloak_user["temporary_password"],
    }


async def disable_tenant_user(
    *, session: AsyncSession, identity: IdentityContext, user_id: str, request_id: str
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can disable users.")
    tenant_admins = (
        await session.execute(
            select(func.count())
            .select_from(
                users.join(user_roles, user_roles.c.user_id == users.c.id).join(
                    roles, roles.c.id == user_roles.c.role_id
                )
            )
            .where(
                users.c.tenant_id == identity.tenant.tenant_id,
                users.c.is_active.is_(True),
                roles.c.name == "tenant_admin",
            )
        )
    ).scalar_one()
    target_is_admin = (
        await session.execute(
            select(roles.c.name)
            .select_from(user_roles.join(roles, roles.c.id == user_roles.c.role_id))
            .where(user_roles.c.user_id == user_id, roles.c.name == "tenant_admin")
        )
    ).first()
    if target_is_admin and tenant_admins <= 1:
        raise ValueError("The final tenant administrator cannot be disabled.")
    await session.execute(
        update(users)
        .where(users.c.id == user_id, users.c.tenant_id == identity.tenant.tenant_id)
        .values(is_active=False)
    )
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=identity.user_id,
        request_id=request_id,
        event_type="User Disabled",
        resource_type="user",
        resource_id=user_id,
    )
    return {"user_id": user_id, "disabled": True}
