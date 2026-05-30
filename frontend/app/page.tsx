import {
  ArrowRight,
  BarChart3,
  FileCheck2,
  LockKeyhole,
  SearchCheck,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui";

const outcomes = [
  ["Less time searching", "Employees get answers from approved policies instead of digging through folders."],
  ["Controlled access", "Sensitive documents stay visible only to the roles that are allowed to retrieve them."],
  ["Answers with sources", "Every answer is grounded in citations, evidence, and hallucination checks."],
  ["Operational visibility", "Admins can inspect documents, lifecycle state, retrieval diagnostics, and governance status."]
];

const features: Array<{ label: string; Icon: LucideIcon }> = [
  { label: "RBAC before retrieval", Icon: LockKeyhole },
  { label: "Hybrid BM25 + vector search", Icon: SearchCheck },
  { label: "Grounded citations", Icon: FileCheck2 },
  { label: "Tenant isolation", Icon: ShieldCheck },
  { label: "Hallucination prevention", Icon: Sparkles },
  { label: "Observability ready", Icon: BarChart3 }
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#f7f8fb]">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="text-lg font-semibold tracking-tight">ACME Knowledge AI</Link>
          <nav className="hidden items-center gap-6 text-sm text-slate-600 md:flex">
            <a href="#how">How it works</a>
            <a href="#security">Security</a>
            <a href="#outcomes">Outcomes</a>
          </nav>
          <Link className="rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white" href="/organization">
            Enter Workspace
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-20">
        <div>
          <Badge tone="accent">Security-first enterprise RAG</Badge>
          <h1 className="mt-5 max-w-4xl text-4xl font-semibold leading-tight tracking-normal text-slate-950 sm:text-5xl">
            AI knowledge answers for enterprise teams, governed by access control.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600">
            Upload company policies, assign document visibility by role, and let employees ask questions only against the files they are authorized to retrieve.
          </p>
          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <Link className="inline-flex items-center justify-center gap-2 rounded-md bg-teal-700 px-5 py-3 text-sm font-semibold text-white" href="/organization">
              Start Demo Workspace <ArrowRight className="h-4 w-4" />
            </Link>
            <a className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-medium" href="#how">
              See how retrieval is governed
            </a>
          </div>
          <div className="mt-6 text-sm text-slate-500">Local-first demo. Keycloak identity. Postgres metadata. Qdrant retrieval.</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="rounded-lg bg-slate-950 p-4 text-white">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium">Answer Preview</span>
              <Badge tone="success">Grounded</Badge>
            </div>
            <div className="rounded-md bg-white/10 p-3 text-sm text-slate-100">
              Who gets VPN access?
            </div>
            <div className="mt-3 rounded-md bg-teal-500/15 p-3 text-sm leading-6 text-teal-50">
              VPN access is required for remote employees <span className="font-semibold">[c1]</span>.
            </div>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {features.map(({ label, Icon }) => (
              <div key={label} className="flex items-center gap-2 rounded-md border border-slate-200 p-3 text-sm">
                <Icon className="h-4 w-4 text-teal-700" />
                {label}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="text-2xl font-semibold">How secure enterprise retrieval works</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              The platform never retrieves first and checks permissions later. It validates identity, resolves tenant context, filters by document permissions, and only then searches authorized evidence.
            </p>
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-4">
            {["Keycloak login", "Tenant + role resolve", "RBAC document filter", "Hybrid retrieval + citations"].map((step, index) => (
              <div key={step} className="rounded-lg border border-slate-200 p-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-50 text-sm font-semibold text-teal-800">{index + 1}</div>
                <div className="mt-4 font-medium">{step}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="outcomes" className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {outcomes.map(([title, copy]) => (
            <div key={title} className="rounded-lg border border-slate-200 bg-white p-5">
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{copy}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="security" className="bg-slate-950">
        <div className="mx-auto max-w-7xl px-4 py-12 text-white sm:px-6">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold">Designed for governance, not guesswork.</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Frontend roles are only displayed for clarity. The backend validates Keycloak JWTs and enforces tenant isolation and document RBAC before vector search, BM25, reranking, prompts, citations, and hallucination scoring.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
