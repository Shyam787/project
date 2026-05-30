from pydantic import BaseModel, Field

from app.rbac.policies import Permission
from app.tenant.context import TenantContext


class IdentityContext(BaseModel):
    user_id: str = Field(min_length=1)
    email: str | None = None
    tenant: TenantContext
    roles: set[str]
    permissions: set[Permission]
