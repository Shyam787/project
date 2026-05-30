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
        for role_name in ("tenant_admin", "manager", "employee", "viewer"):
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
        for email, role_name, display_name in (
            ("admin@acme.com", "tenant_admin", "ACME Admin"),
            ("manager@acme.com", "manager", "ACME Manager"),
            ("employee@acme.com", "employee", "ACME Employee"),
            ("viewer@acme.com", "viewer", "ACME Viewer"),
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
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await connection.execute(
                insert(user_roles)
                .values(
                    id=f"seed-{email}-{role_name}",
                    tenant_id="acme",
                    user_id=email,
                    role_id=role_ids[role_name],
                )
                .on_conflict_do_nothing(constraint="uq_user_roles_scope")
            )
