from enum import StrEnum


class Permission(StrEnum):
    DOCUMENT_READ = "document_read"
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    ADMIN_MANAGEMENT = "admin_management"
    AUDIT_ACCESS = "audit_access"
    FEEDBACK_ACCESS = "feedback_access"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "super_admin": set(Permission),
    "tenant_admin": set(Permission),
    "manager": {
        Permission.DOCUMENT_READ,
        Permission.FEEDBACK_ACCESS,
    },
    "employee": {
        Permission.DOCUMENT_READ,
        Permission.FEEDBACK_ACCESS,
    },
    "viewer": {Permission.DOCUMENT_READ},
}

GOVERNED_TENANT_ROLES = {"tenant_admin", "manager", "employee", "viewer"}


def permissions_for_roles(roles: set[str]) -> set[Permission]:
    permissions: set[Permission] = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, set()))
    return permissions


def has_permission(roles: set[str], permission: Permission) -> bool:
    return permission in permissions_for_roles(roles)
