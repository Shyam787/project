import re
import shutil
from uuid import uuid4
from pathlib import Path

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import record_audit_event
from app.auth.models import IdentityContext
from app.core.config import Settings
from app.db.schema import audit_logs, chunks, conversations, document_permissions, documents, feedback, hallucination_results, messages, roles, tenants, user_roles, users
from app.platform.keycloak_admin import KeycloakAdminClient
from app.retrieval.qdrant_store import QdrantVectorStore

DEFAULT_ROLES = {"tenant_admin", "manager", "employee", "hr", "finance", "security"}
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


def validate_confirmation_password(*, tenant_id: str, confirmation: str) -> None:
    expected = f"{tenant_id}-admin"
    if confirmation != expected:
        raise ValueError("Confirmation password is incorrect for this organization.")


async def identity_db_user_id(
    *, session: AsyncSession, identity: IdentityContext
) -> str | None:
    row = (
        await session.execute(
            select(users.c.id).where(
                users.c.tenant_id == identity.tenant.tenant_id,
                (
                    (users.c.external_subject == identity.user_id)
                    | (users.c.id == identity.user_id)
                    | (users.c.email == (identity.email or ""))
                ),
            )
        )
    ).first()
    return row.id if row is not None else None


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


async def login_status_for_email(*, session: AsyncSession, email: str) -> dict:
    row = (
        await session.execute(
            select(users.c.is_active).where(func.lower(users.c.email) == email.lower())
        )
    ).first()
    if row is None:
        return {"exists": False, "is_active": False}
    return {"exists": True, "is_active": bool(row.is_active)}


async def create_tenant_user(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    identity: IdentityContext,
    full_name: str,
    email: str,
    role: str,
    password: str,
    confirm_password: str,
    is_active: bool,
    request_id: str,
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can create users.")
    if role not in DEFAULT_ROLES:
        raise ValueError("Unsupported role.")
    if password != confirm_password:
        raise ValueError("Password and confirmation do not match.")
    validate_password(password)
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
        password=password,
        temporary=False,
        enabled=is_active,
    )
    await session.execute(
        insert(users)
        .values(
            id=keycloak_user["keycloak_id"],
            tenant_id=identity.tenant.tenant_id,
            external_subject=keycloak_user["keycloak_id"],
            email=email,
            display_name=full_name,
            is_active=is_active,
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
    actor_user_id = await identity_db_user_id(session=session, identity=identity)
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=actor_user_id,
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
        "is_active": is_active,
    }


async def update_tenant_user(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    identity: IdentityContext,
    user_id: str,
    full_name: str,
    role: str,
    is_active: bool,
    password: str | None,
    request_id: str,
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can update users.")
    if role not in DEFAULT_ROLES:
        raise ValueError("Unsupported role.")
    if password:
        validate_password(password)
    row = (
        await session.execute(
            select(users.c.email, users.c.is_active, users.c.external_subject).where(
                users.c.id == user_id,
                users.c.tenant_id == identity.tenant.tenant_id,
            )
        )
    ).first()
    if row is None:
        raise ValueError("User not found.")
    actor_user_id = await identity_db_user_id(session=session, identity=identity)
    if user_id == actor_user_id and not is_active:
        raise ValueError("You cannot deactivate your own administrator account.")
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
    await keycloak.update_user(
        user_id=row.external_subject,
        full_name=full_name,
        tenant_id=identity.tenant.tenant_id,
        roles={role},
        enabled=is_active,
        password=password,
    )
    await session.execute(
        update(users)
        .where(users.c.id == user_id, users.c.tenant_id == identity.tenant.tenant_id)
        .values(display_name=full_name, is_active=is_active)
    )
    await session.execute(
        delete(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.tenant_id == identity.tenant.tenant_id,
        )
    )
    await session.execute(
        insert(user_roles).values(
            id=str(uuid4()),
            tenant_id=identity.tenant.tenant_id,
            user_id=user_id,
            role_id=role_row.id,
        )
    )
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=actor_user_id,
        request_id=request_id,
        event_type="User Updated",
        resource_type="user",
        resource_id=user_id,
        metadata={"role": role, "is_active": is_active},
    )
    return {"user_id": user_id, "email": row.email, "role": role, "is_active": is_active}


async def delete_tenant_user(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    identity: IdentityContext,
    user_id: str,
    confirmation_password: str,
    request_id: str,
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can delete users.")
    validate_confirmation_password(
        tenant_id=identity.tenant.tenant_id,
        confirmation=confirmation_password,
    )
    row = (
        await session.execute(
            select(users.c.is_active, users.c.external_subject).where(
                users.c.id == user_id,
                users.c.tenant_id == identity.tenant.tenant_id,
            )
        )
    ).first()
    if row is None:
        raise ValueError("User not found.")
    if row.is_active:
        raise ValueError("User is active. Set the user to inactive before deleting.")
    actor_user_id = await identity_db_user_id(session=session, identity=identity)
    if user_id == actor_user_id:
        raise ValueError("You cannot delete your own administrator account.")
    await keycloak.delete_user(user_id=row.external_subject)
    await session.execute(delete(user_roles).where(user_roles.c.user_id == user_id, user_roles.c.tenant_id == identity.tenant.tenant_id))
    await session.execute(update(audit_logs).where(audit_logs.c.user_id == user_id, audit_logs.c.tenant_id == identity.tenant.tenant_id).values(user_id=None))
    await session.execute(delete(users).where(users.c.id == user_id, users.c.tenant_id == identity.tenant.tenant_id))
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=actor_user_id,
        request_id=request_id,
        event_type="User Deleted",
        resource_type="user",
        resource_id=user_id,
    )
    return {"user_id": user_id, "deleted": True}


async def delete_organization(
    *,
    session: AsyncSession,
    keycloak: KeycloakAdminClient,
    vector_store: QdrantVectorStore,
    identity: IdentityContext,
    confirmation_password: str,
    settings: Settings,
) -> dict:
    if "tenant_admin" not in identity.roles:
        raise PermissionError("Only tenant administrators can delete organizations.")
    tenant_id = identity.tenant.tenant_id
    validate_confirmation_password(tenant_id=tenant_id, confirmation=confirmation_password)
    document_rows = (
        await session.execute(
            select(documents.c.id, documents.c.storage_uri).where(documents.c.tenant_id == tenant_id)
        )
    ).all()
    for document_id, storage_uri in document_rows:
        await vector_store.delete_document(tenant_id=tenant_id, document_id=document_id)
        if storage_uri:
            Path(storage_uri).unlink(missing_ok=True)
    user_rows = (await session.execute(select(users.c.external_subject).where(users.c.tenant_id == tenant_id))).all()
    for row in user_rows:
        await keycloak.delete_user(user_id=row.external_subject)
    await session.execute(delete(hallucination_results).where(hallucination_results.c.tenant_id == tenant_id))
    await session.execute(delete(feedback).where(feedback.c.tenant_id == tenant_id))
    await session.execute(delete(messages).where(messages.c.tenant_id == tenant_id))
    await session.execute(delete(conversations).where(conversations.c.tenant_id == tenant_id))
    await session.execute(delete(chunks).where(chunks.c.tenant_id == tenant_id))
    await session.execute(delete(document_permissions).where(document_permissions.c.tenant_id == tenant_id))
    await session.execute(delete(documents).where(documents.c.tenant_id == tenant_id))
    await session.execute(delete(audit_logs).where(audit_logs.c.tenant_id == tenant_id))
    await session.execute(delete(user_roles).where(user_roles.c.tenant_id == tenant_id))
    await session.execute(delete(users).where(users.c.tenant_id == tenant_id))
    await session.execute(delete(roles).where(roles.c.tenant_id == tenant_id))
    await session.execute(delete(tenants).where(tenants.c.id == tenant_id))
    shutil.rmtree(Path(settings.storage_root) / tenant_id, ignore_errors=True)
    return {"tenant_id": tenant_id, "deleted": True}


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
    actor_user_id = await identity_db_user_id(session=session, identity=identity)
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=actor_user_id,
        request_id=request_id,
        event_type="User Disabled",
        resource_type="user",
        resource_id=user_id,
    )
    return {"user_id": user_id, "disabled": True}
