from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.cache.redis_cache import tenant_cache_key
from app.auth.models import IdentityContext
from app.db.schema import CORE_TABLE_NAMES, metadata
from app.rbac.policies import Permission
from app.tenant.context import resolve_tenant_context


def test_core_tables_match_documented_schema():
    assert set(CORE_TABLE_NAMES) == {
        "tenants",
        "users",
        "roles",
        "documents",
        "document_permissions",
        "chunks",
        "conversations",
        "messages",
        "feedback",
        "audit_logs",
        "hallucination_results",
    }


def test_all_protected_tables_are_tenant_scoped():
    for table in metadata.sorted_tables:
        if table.name == "tenants":
            continue
        assert "tenant_id" in table.c, table.name
        assert table.c.tenant_id.nullable is False


def test_postgres_schema_compiles():
    dialect = postgresql.dialect()
    compiled = "\n".join(
        str(CreateTable(table).compile(dialect=dialect))
        for table in metadata.sorted_tables
    )
    assert "tenant_id" in compiled


def test_cache_keys_include_tenant_and_rbac_scope():
    identity = IdentityContext(
        user_id="user-1",
        tenant=resolve_tenant_context("tenant-a"),
        roles={"employee"},
        permissions={Permission.DOCUMENT_READ},
    )

    key = tenant_cache_key(
        identity=identity,
        category="query_response",
        parts={"query": "policy"},
    )

    assert key.startswith("tenant:tenant-a:rbac:")
    assert ":query_response:" in key
