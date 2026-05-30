from pydantic import BaseModel, Field


class TenantContext(BaseModel):
    tenant_id: str = Field(min_length=1)
    namespace: str = Field(min_length=1)


def resolve_tenant_context(tenant_id: str) -> TenantContext:
    return TenantContext(tenant_id=tenant_id, namespace=f"tenant_{tenant_id}")
