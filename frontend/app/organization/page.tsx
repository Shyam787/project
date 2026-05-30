import { ArrowRight, Building2, CheckCircle2, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui";

export default function OrganizationPage() {
  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-8 sm:px-6">
      <div className="mx-auto max-w-5xl">
        <Link className="text-sm text-slate-500" href="/">Back to overview</Link>
        <section className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <Badge tone="accent">Organization Access</Badge>
            <h1 className="mt-4 text-3xl font-semibold tracking-normal">Select your enterprise workspace</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Organizations own documents, user roles, and retrieval boundaries. This demo uses ACME Corporation as the active tenant workspace.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-teal-50 text-teal-800">
                <Building2 className="h-6 w-6" />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="text-xl font-semibold">ACME Corporation</h2>
                <p className="mt-1 text-sm text-slate-600">Tenant ID: tenant-acme</p>
                <div className="mt-4 grid gap-2 text-sm text-slate-600">
                  <div className="flex gap-2"><CheckCircle2 className="h-4 w-4 text-teal-700" /> Keycloak-managed users and roles</div>
                  <div className="flex gap-2"><ShieldCheck className="h-4 w-4 text-teal-700" /> Documents isolated inside this workspace</div>
                  <div className="flex gap-2"><CheckCircle2 className="h-4 w-4 text-teal-700" /> RBAC enforced before retrieval</div>
                </div>
                <Link className="mt-5 inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white" href="/login">
                  Continue to employee login <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
