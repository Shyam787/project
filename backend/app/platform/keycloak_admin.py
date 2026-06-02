import secrets
import string

import httpx

from app.core.config import Settings


def split_keycloak_name(full_name: str) -> tuple[str, str]:
    first_name, _, last_name = full_name.strip().partition(" ")
    return first_name or full_name.strip(), last_name or "User"


class KeycloakAdminClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def _admin_token(self) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self._settings.keycloak_base_url}/realms/master/protocol/openid-connect/token",
                data={
                    "client_id": "admin-cli",
                    "username": self._settings.keycloak_admin_username,
                    "password": self._settings.keycloak_admin_password,
                    "grant_type": "password",
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def create_user(
        self,
        *,
        email: str,
        full_name: str,
        tenant_id: str,
        roles: set[str],
        password: str | None = None,
        temporary: bool = False,
        enabled: bool = True,
    ) -> dict:
        token = await self._admin_token()
        password_value = password or generate_temporary_password()
        first_name, last_name = split_keycloak_name(full_name)
        payload = {
            "username": email,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": enabled,
            "emailVerified": True,
            "attributes": {"tenant_id": tenant_id},
            "credentials": [
                {
                    "type": "password",
                    "value": password_value,
                    "temporary": temporary,
                }
            ],
        }
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=20) as client:
            created = await client.post(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users",
                headers=headers,
                json=payload,
            )
            if created.status_code == 409:
                raise ValueError("A user with this email already exists.")
            created.raise_for_status()
            lookup = await client.get(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users",
                headers=headers,
                params={"username": email, "exact": "true"},
            )
            lookup.raise_for_status()
            users = lookup.json()
            if not users:
                raise ValueError("Keycloak user creation did not return a user.")
            user_id = users[0]["id"]
            user_payload = users[0]
            user_payload["attributes"] = {"tenant_id": tenant_id}
            update_user = await client.put(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}",
                headers=headers,
                json=user_payload,
            )
            update_user.raise_for_status()
            realm_roles = await client.get(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/roles",
                headers=headers,
            )
            realm_roles.raise_for_status()
            roles_by_name = {role["name"]: role for role in realm_roles.json()}
            role_payload = [roles_by_name[role] for role in roles if role in roles_by_name]
            if role_payload:
                assign = await client.post(
                    f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}/role-mappings/realm",
                    headers=headers,
                    json=role_payload,
                )
                assign.raise_for_status()
        return {"keycloak_id": user_id, "email": email, "temporary_password": password_value}

    async def update_user(
        self,
        *,
        user_id: str,
        full_name: str,
        tenant_id: str,
        roles: set[str],
        enabled: bool,
        password: str | None = None,
    ) -> None:
        token = await self._admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        first_name, last_name = split_keycloak_name(full_name)
        async with httpx.AsyncClient(timeout=20) as client:
            current = await client.get(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}",
                headers=headers,
            )
            current.raise_for_status()
            payload = current.json()
            payload.update(
                {
                    "firstName": first_name,
                    "lastName": last_name,
                    "enabled": enabled,
                    "attributes": {"tenant_id": tenant_id},
                }
            )
            updated = await client.put(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}",
                headers=headers,
                json=payload,
            )
            updated.raise_for_status()
            realm_roles = await client.get(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/roles",
                headers=headers,
            )
            realm_roles.raise_for_status()
            roles_by_name = {role["name"]: role for role in realm_roles.json()}
            existing = await client.get(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}/role-mappings/realm",
                headers=headers,
            )
            existing.raise_for_status()
            removable = [
                role
                for role in existing.json()
                if role.get("name")
                in {"tenant_admin", "manager", "employee", "hr", "finance", "security", "viewer"}
            ]
            if removable:
                remove = await client.request(
                    "DELETE",
                    f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}/role-mappings/realm",
                    headers=headers,
                    json=removable,
                )
                remove.raise_for_status()
            role_payload = [roles_by_name[role] for role in roles if role in roles_by_name]
            if role_payload:
                assign = await client.post(
                    f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}/role-mappings/realm",
                    headers=headers,
                    json=role_payload,
                )
                assign.raise_for_status()
            if password:
                reset = await client.put(
                    f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}/reset-password",
                    headers=headers,
                    json={"type": "password", "value": password, "temporary": False},
                )
                reset.raise_for_status()

    async def delete_user(self, *, user_id: str) -> None:
        token = await self._admin_token()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.delete(
                f"{self._settings.keycloak_base_url}/admin/realms/{self._settings.keycloak_realm}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code not in {204, 404}:
                response.raise_for_status()


def generate_temporary_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        value = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(char.isupper() for char in value)
            and any(char.islower() for char in value)
            and any(char.isdigit() for char in value)
            and any(char in "!@#$%^&*" for char in value)
        ):
            return value
