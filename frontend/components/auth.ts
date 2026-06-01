"use client";

export type SessionClaims = {
  subject: string;
  tenant: string;
  email: string;
  fullName?: string;
  roles: string[];
};

export const TOKEN_KEY = "enterprise_rag_token";
export const USER_KEY = "enterprise_rag_user";
const governedRoles = new Set(["tenant_admin", "manager", "employee", "viewer"]);

export function readClaims(token: string): SessionClaims | null {
  try {
    const payload = token.split(".")[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const claims = JSON.parse(atob(normalized));
    const roles = [
      ...(claims.roles ?? []),
      ...(claims.realm_access?.roles ?? []),
      ...(claims.resource_access?.["enterprise-rag-api"]?.roles ?? [])
    ];
    return {
      subject: claims.preferred_username ?? claims.sub ?? "authenticated-user",
      email: claims.email ?? claims.preferred_username ?? "",
      fullName: claims.name ?? ([claims.given_name, claims.family_name].filter(Boolean).join(" ") || undefined),
      tenant: claims.tenant_id ?? "unknown-tenant",
      roles: Array.from(new Set(roles.filter((role) => governedRoles.has(role)))).sort()
    };
  } catch {
    return null;
  }
}

export function getStoredToken() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(TOKEN_KEY) ?? "";
}

export function storeToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function isTenantAdmin(claims: SessionClaims | null) {
  return Boolean(claims?.roles.includes("tenant_admin"));
}
