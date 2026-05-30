"use client";

export type SessionClaims = {
  subject: string;
  tenant: string;
  roles: string[];
};

export const TOKEN_KEY = "enterprise_rag_token";
export const USER_KEY = "enterprise_rag_user";

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
      tenant: claims.tenant_id ?? "unknown-tenant",
      roles: Array.from(new Set(roles)).sort()
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
