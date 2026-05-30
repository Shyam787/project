"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, CheckCircle2, Circle } from "lucide-react";
import { Badge } from "@/components/ui";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function SignupClient() {
  const router = useRouter();
  const [form, setForm] = useState({
    organization_name: "",
    organization_id: "",
    admin_full_name: "",
    admin_email: "",
    password: "",
    confirm_password: ""
  });
  const [status, setStatus] = useState("");
  const [statusTone, setStatusTone] = useState<"info" | "error" | "success">("info");
  const [loading, setLoading] = useState(false);
  const passwordStarted = form.password.length > 0;
  const checks = useMemo(() => [
    ["Minimum 12 characters", form.password.length >= 12],
    ["Contains uppercase letter", /[A-Z]/.test(form.password)],
    ["Contains lowercase letter", /[a-z]/.test(form.password)],
    ["Contains number", /\d/.test(form.password)],
    ["Contains special character", /[^A-Za-z0-9]/.test(form.password)]
  ], [form.password]);

  function update(key: keyof typeof form, value: string) {
    setForm((current) => ({
      ...current,
      [key]: key === "organization_id" ? value.toLowerCase().replace(/[^a-z0-9-]/g, "") : value
    }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setStatusTone("info");
    setStatus("Creating organization, tenant, roles, and administrator...");
    const response = await fetch(`${apiBase}/api/v1/organizations/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    const body = await response.json();
    setLoading(false);
    if (!response.ok) {
      setStatusTone("error");
      setStatus(body.error?.message ?? body.detail ?? "Organization creation failed.");
      return;
    }
    setStatusTone("success");
    setStatus("Organization created. Redirecting to sign in...");
    setTimeout(() => router.push("/login"), 800);
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-8 sm:px-6">
      <div className="mx-auto max-w-5xl">
        <Link className="text-sm text-slate-500" href="/">Back to home</Link>
        <div className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <section>
            <Badge tone="accent">Organization Onboarding</Badge>
            <h1 className="mt-4 text-3xl font-semibold tracking-normal">Create your Enterprise RAG organization</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              This creates an isolated tenant, default roles, and the first tenant administrator. Users sign in with email and password; tenant context is loaded from Keycloak claims.
            </p>
          </section>
          <form className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" onSubmit={submit}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Organization Name" value={form.organization_name} onChange={(value) => update("organization_name", value)} />
              <Field label="Organization ID" value={form.organization_id} onChange={(value) => update("organization_id", value)} placeholder="company-id" />
              <Field label="Admin Full Name" value={form.admin_full_name} onChange={(value) => update("admin_full_name", value)} />
              <Field label="Admin Email" type="email" value={form.admin_email} onChange={(value) => update("admin_email", value)} />
              <Field label="Password" type="password" value={form.password} onChange={(value) => update("password", value)} />
              <Field label="Confirm Password" type="password" value={form.confirm_password} onChange={(value) => update("confirm_password", value)} />
            </div>
            <div className="mt-4 grid gap-2 rounded-lg bg-slate-50 p-3 text-sm">
              {checks.map(([label, passed]) => (
                <div key={String(label)} className={!passwordStarted ? "text-slate-500" : passed ? "text-teal-700" : "text-red-700"}>
                  {passwordStarted && passed ? <CheckCircle2 className="mr-2 inline h-4 w-4" /> : <Circle className="mr-2 inline h-4 w-4" />}{label}
                </div>
              ))}
            </div>
            <button disabled={loading} className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? "Creating..." : "Create organization"} <ArrowRight className="h-4 w-4" />
            </button>
            <div className="mt-4 text-center text-sm text-slate-600">
              Organization already exists? <Link className="font-semibold text-teal-700" href="/login">Sign in</Link>
            </div>
            {status ? <div className={`mt-3 rounded-md border p-3 text-sm ${statusTone === "error" ? "border-red-200 bg-red-50 text-red-800" : statusTone === "success" ? "border-teal-200 bg-teal-50 text-teal-800" : "border-slate-200 bg-slate-50 text-slate-600"}`}>{status}</div> : null}
          </form>
        </div>
      </div>
    </main>
  );
}

function Field({ label, value, onChange, type = "text", placeholder = "" }: { label: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string }) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <input required className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" type={type} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
