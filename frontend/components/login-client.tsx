"use client";

import { FormEvent, useState } from "react";
import { Eye, KeyRound, LogIn } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui";
import { readClaims, storeTokens } from "@/components/auth";

const keycloakBase = process.env.NEXT_PUBLIC_KEYCLOAK_BASE_URL ?? "http://localhost:8081";
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function LoginClient() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("");
  const [statusTone, setStatusTone] = useState<"info" | "error" | "success">("info");
  const [loading, setLoading] = useState(false);

  async function login(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setStatusTone("info");
    setStatus("Signing in...");
    const response = await fetch(`${keycloakBase}/realms/enterprise-rag/protocol/openid-connect/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: "enterprise-rag-api",
        username,
        password,
        grant_type: "password"
      })
    });
    const body = await response.json();
    setLoading(false);
    if (!response.ok) {
      const details = String(body.error_description ?? body.error ?? "").toLowerCase();
      setStatusTone("error");
      if (details.includes("disabled") || details.includes("inactive")) {
        setStatus("Your account is inactive. Contact your organization administrator to regain access.");
      } else if (details.includes("not fully set up")) {
        setStatus("Your account exists but is not fully set up. Ask your organization administrator to save your profile or reset your password.");
      } else {
        try {
          const lookup = await fetch(`${apiBase}/api/v1/users/login-status?email=${encodeURIComponent(username)}`);
          const lookupBody = await lookup.json();
          if (lookup.ok && lookupBody.payload?.exists && lookupBody.payload?.is_active) {
            setStatus("The password is incorrect for this user. Ask your organization administrator to reset it if needed.");
          } else if (lookup.ok && lookupBody.payload?.exists && !lookupBody.payload?.is_active) {
            setStatus("Your account is inactive. Contact your organization administrator to regain access.");
          } else {
            setStatus("No account was found for this email address. Use the login email created by your organization admin.");
          }
        } catch {
          setStatus("Unable to verify this sign-in. Check the email address and password, then try again.");
        }
      }
      return;
    }
    storeTokens(body.access_token, body.refresh_token);
    const claims = readClaims(body.access_token);
    setStatusTone("success");
    setStatus(`Authenticated as ${claims?.subject ?? username}. Redirecting to workspace...`);
    router.push("/workspace");
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-8 sm:px-6">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <section>
          <Link className="text-sm text-slate-500" href="/">Back to home</Link>
          <Badge tone="accent">Secure Workspace</Badge>
          <h1 className="mt-4 text-3xl font-semibold tracking-normal">Sign in to your knowledge workspace</h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
            Use the email address and password provided by your organization administrator to access your secure document workspace.
          </p>
          <div className="mt-5 rounded-lg border border-teal-200 bg-teal-50 p-4 text-sm text-teal-900">
            <div className="font-semibold">Need access?</div>
            <p className="mt-2 leading-6">Ask your organization administrator to create your account and share your sign-in details.</p>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <form className="space-y-3" onSubmit={login}>
            <label className="block text-sm font-medium">Email</label>
            <input className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" type="email" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="name@company.com" required />
            <label className="block text-sm font-medium">Password</label>
            <div className="flex gap-2">
              <input className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} />
              <button className="rounded-md border border-slate-300 px-3" type="button" onClick={() => setShowPassword(!showPassword)} title="Show password">
                <Eye className="h-4 w-4" />
              </button>
            </div>
            <button disabled={loading} className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? <KeyRound className="h-4 w-4 animate-pulse" /> : <LogIn className="h-4 w-4" />}
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          {status ? <div className={`mt-4 rounded-md border p-3 text-sm ${statusTone === "error" ? "border-red-200 bg-red-50 text-red-800" : statusTone === "success" ? "border-teal-200 bg-teal-50 text-teal-800" : "border-slate-200 bg-slate-50 text-slate-600"}`}>{status}</div> : null}
        </section>
      </div>
    </main>
  );
}
