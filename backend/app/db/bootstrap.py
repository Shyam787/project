from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.dialects.postgresql import insert

from app.db.schema import metadata, roles, tenants, user_roles, users


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.execute(
            insert(tenants)
            .values(id="synycs", name="Synycs Group", slug="synycs")
            .on_conflict_do_nothing(index_elements=["id"])
        )
        role_ids: dict[str, str] = {}
        for role_name in ("tenant_admin", "manager", "employee", "hr", "finance", "security"):
            role_id = f"seed-synycs-{role_name}"
            role_ids[role_name] = role_id
            await connection.execute(
                insert(roles)
                .values(
                    id=role_id,
                    tenant_id="synycs",
                    name=role_name,
                    description=f"{role_name} seed role",
                )
                .on_conflict_do_nothing(constraint="uq_roles_tenant_name")
            )
            row = (
                await connection.execute(
                    select(roles.c.id).where(
                        roles.c.tenant_id == "synycs",
                        roles.c.name == role_name,
                    )
                )
            ).first()
            if row is not None:
                role_ids[role_name] = row.id
        for email, role_name, display_name in (
            ("admin@synycs.com", "tenant_admin", "Synycs Admin"),
            ("manager@synycs.com", "manager", "Synycs Manager"),
            ("employee@synycs.com", "employee", "Synycs Employee"),
            ("shyam@synycs.com", "hr", "Shyam HR"),
            ("malli@synycs.com", "finance", "Mallikarjun Finance"),
            ("esh@synycs.com", "security", "Esh Security"),
        ):
            await connection.execute(
                insert(users)
                .values(
                    id=email,
                    tenant_id="synycs",
                    external_subject=email,
                    email=email,
                    display_name=display_name,
                )
                .on_conflict_do_nothing(constraint="uq_users_tenant_email")
            )
            user_row = (
                await connection.execute(
                    select(users.c.id).where(
                        users.c.tenant_id == "synycs",
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
                    tenant_id="synycs",
                    user_id=user_id,
                    role_id=role_ids[role_name],
                )
                .on_conflict_do_nothing(constraint="uq_user_roles_scope")
            )
