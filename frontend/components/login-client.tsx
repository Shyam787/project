"use client";

import { FormEvent, useState } from "react";
import { Eye, KeyRound, LogIn, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui";
import { readClaims, storeToken } from "@/components/auth";

const keycloakBase = process.env.NEXT_PUBLIC_KEYCLOAK_BASE_URL ?? "http://localhost:8081";

const demoUsers = {
  admin: { label: "Tenant Admin", username: "demo-admin", password: "DemoAdmin123!", detail: "Upload, classify, archive, delete, evaluate, and query governed documents." },
  viewer: { label: "Viewer", username: "demo-viewer", password: "DemoViewer123!", detail: "Ask questions and inspect citations for viewer-approved documents only." }
};

export function LoginClient() {
  const router = useRouter();
  const [username, setUsername] = useState("demo-admin");
  const [password, setPassword] = useState("DemoAdmin123!");
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function login(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setStatus("Signing in through ACME Keycloak...");
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
      setStatus("Incorrect username or password. Please verify your credentials and try again.");
      return;
    }
    storeToken(body.access_token);
    const claims = readClaims(body.access_token);
    setStatus(`Authenticated as ${claims?.subject ?? username}. Redirecting to workspace...`);
    router.push("/workspace");
  }

  function chooseDemo(kind: keyof typeof demoUsers) {
    setUsername(demoUsers[kind].username);
    setPassword(demoUsers[kind].password);
    setStatus(`${demoUsers[kind].label} selected.`);
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-8 sm:px-6">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <section>
          <Link className="text-sm text-slate-500" href="/organization">Back to organization</Link>
          <Badge tone="accent">Employee Login</Badge>
          <h1 className="mt-4 text-3xl font-semibold tracking-normal">Sign in to ACME Knowledge AI</h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
            Authentication is delegated to the organization identity provider. The backend validates the signed Keycloak token and reads tenant and role claims from it.
          </p>
          <div className="mt-5 rounded-lg border border-teal-200 bg-teal-50 p-4 text-sm text-teal-900">
            <div className="flex items-center gap-2 font-semibold"><ShieldCheck className="h-4 w-4" /> Why this matters</div>
            <p className="mt-2 leading-6">The frontend can display roles, but the backend enforces them. Unauthorized documents never reach retrieval or answer generation.</p>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-3 sm:grid-cols-2">
            {(["admin", "viewer"] as const).map((kind) => (
              <button key={kind} type="button" onClick={() => chooseDemo(kind)} className="rounded-lg border border-slate-200 p-4 text-left hover:border-teal-300">
                <div className="font-semibold">{demoUsers[kind].label}</div>
                <div className="mt-1 text-sm text-slate-500">{demoUsers[kind].username}</div>
                <p className="mt-2 text-xs leading-5 text-slate-600">{demoUsers[kind].detail}</p>
              </button>
            ))}
          </div>

          <form className="mt-5 space-y-3" onSubmit={login}>
            <label className="block text-sm font-medium">Username</label>
            <input className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={username} onChange={(event) => setUsername(event.target.value)} />
            <label className="block text-sm font-medium">Password</label>
            <div className="flex gap-2">
              <input className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} />
              <button className="rounded-md border border-slate-300 px-3" type="button" onClick={() => setShowPassword(!showPassword)} title="Show password">
                <Eye className="h-4 w-4" />
              </button>
            </div>
            <div className="text-xs text-slate-500">Demo password rules: 8+ characters, mixed case, number, and special character.</div>
            <button disabled={loading} className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? <KeyRound className="h-4 w-4 animate-pulse" /> : <LogIn className="h-4 w-4" />}
              {loading ? "Signing in..." : "Sign in with Keycloak"}
            </button>
          </form>
          {status ? <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">{status}</div> : null}
        </section>
      </div>
    </main>
  );
}
