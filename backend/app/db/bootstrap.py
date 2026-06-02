from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.dialects.postgresql import insert

from app.db.schema import metadata, roles, tenants, user_roles, users


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.execute(
            insert(tenants)
            .values(id="acme", name="ACME Corporation", slug="acme")
            .on_conflict_do_nothing(index_elements=["id"])
        )
        role_ids: dict[str, str] = {}
        for role_name in ("tenant_admin", "manager", "employee", "hr", "finance", "security"):
            role_id = f"seed-acme-{role_name}"
            role_ids[role_name] = role_id
            await connection.execute(
                insert(roles)
                .values(
                    id=role_id,
                    tenant_id="acme",
                    name=role_name,
                    description=f"{role_name} seed role",
                )
                .on_conflict_do_nothing(constraint="uq_roles_tenant_name")
            )
            row = (
                await connection.execute(
                    select(roles.c.id).where(
                        roles.c.tenant_id == "acme",
                        roles.c.name == role_name,
                    )
                )
            ).first()
            if row is not None:
                role_ids[role_name] = row.id
        for email, role_name, display_name in (
            ("admin@acme.com", "tenant_admin", "ACME Admin"),
            ("manager@acme.com", "manager", "ACME Manager"),
            ("employee@acme.com", "employee", "ACME Employee"),
            ("hr@acme.com", "hr", "ACME HR"),
            ("finance@acme.com", "finance", "ACME Finance"),
            ("security@acme.com", "security", "ACME Security"),
        ):
            await connection.execute(
                insert(users)
                .values(
                    id=email,
                    tenant_id="acme",
                    external_subject=email,
                    email=email,
                    display_name=display_name,
                )
                .on_conflict_do_nothing(constraint="uq_users_tenant_email")
            )
            user_row = (
                await connection.execute(
                    select(users.c.id).where(
                        users.c.tenant_id == "acme",
                        users.c.email == email,
                    )
                )
            ).first()
            if user_row is None:
                continue
            user_id = user_row.id
            await connection.execute(
                insert(user_roles)
                .values(
                    id=f"seed-{user_id}-{role_name}",
                    tenant_id="acme",
                    user_id=user_id,
                    role_id=role_ids[role_name],
                )
                .on_conflict_do_nothing(constraint="uq_user_roles_scope")
            )
