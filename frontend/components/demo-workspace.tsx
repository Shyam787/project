"use client";

import { FormEvent, useMemo, useState } from "react";
import { MessageSquareText, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui";

const demoRoles = [
  { id: "viewer", label: "Viewer", detail: "General policies" },
  { id: "employee", label: "Employee", detail: "Internal knowledge" },
  { id: "manager", label: "Manager", detail: "Team governance" },
  { id: "tenant_admin", label: "Admin", detail: "Restricted access" }
];

const demoDocs = [
  {
    filename: "Access Control Policy",
    classification: "Internal",
    roles: ["viewer", "employee", "manager", "tenant_admin"],
    lines: [
      "Passwords must contain minimum 14 characters, one uppercase letter, one lowercase letter, one number, and one special character.",
      "VPN access is required for remote employees.",
      "Access reviews are conducted every 90 days.",
      "Document Classification: Internal."
    ]
  },
  {
    filename: "Payroll Approval Policy",
    classification: "Restricted",
    roles: ["tenant_admin"],
    lines: [
      "Only tenant administrators may approve payroll exports.",
      "Payroll reports are retained for seven years.",
      "Document Classification: Restricted."
    ]
  },
  {
    filename: "Contractor Policy",
    classification: "Confidential",
    roles: ["manager", "tenant_admin"],
    lines: [
      "Contractors may only access systems approved by their department manager.",
      "Contractor access must be reviewed every 30 days.",
      "Document Classification: Confidential."
    ]
  }
];

type DemoResult = { answer: string; citations: Array<{ id: string; filename: string; classification: string }> };

export function DemoWorkspace() {
  const [role, setRole] = useState("viewer");
  const [query, setQuery] = useState("1. Who gets VPN access? 2. What are password requirements? 3. Who can approve payroll exports? 4. who approves the contractors to access systems?");
  const [result, setResult] = useState<DemoResult | null>(null);
  const accessible = useMemo(() => demoDocs.filter((doc) => doc.roles.includes(role)), [role]);

  function ask(event: FormEvent) {
    event.preventDefault();
    const questions = extractQuestions(query);
    const citations: DemoResult["citations"] = [];
    const answers = questions.map((question, index) => {
      const evidence = findEvidence(question, accessible);
      if (!evidence) {
        return `${index + 1}. No authorized information was found that answers this question.`;
      }
      const citationId = `c${citations.length + 1}`;
      citations.push({ id: citationId, filename: evidence.filename, classification: evidence.classification });
      return `${index + 1}. ${evidence.line.replace(/[.]+$/, "")} [${citationId}].`;
    });
    setResult({ answer: answers.join("\n"), citations });
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-8 sm:px-6">
      <div className="mx-auto max-w-7xl">
        <Link className="text-sm text-slate-500" href="/">Back to home</Link>
        <div className="mt-6 grid gap-5 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
          <section>
            <Badge tone="accent">Interactive Demo Workspace</Badge>
            <h1 className="mt-3 text-3xl font-semibold tracking-normal">Test role-aware retrieval before signing in</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Choose a role, ask a question, and see how restricted documents are excluded before answer generation.
            </p>
            <div className="mt-5 rounded-lg border border-teal-200 bg-teal-50 p-4 text-sm text-teal-900">
              <div className="flex items-center gap-2 font-semibold"><ShieldCheck className="h-4 w-4" /> Demo governance</div>
              <p className="mt-2 leading-6">This page uses synthetic sample documents only. It demonstrates the product behavior without reading tenant data.</p>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <form className="space-y-3" onSubmit={ask}>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-2">
                <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                  {demoRoles.map((item) => (
                    <button
                      className={`rounded-md border bg-white px-3 py-2 text-left transition ${role === item.id ? "border-teal-400 text-teal-900 shadow-sm" : "border-transparent text-slate-600 hover:border-slate-200"}`}
                      key={item.id}
                      onClick={() => { setRole(item.id); setResult(null); }}
                      type="button"
                    >
                      <div className="text-sm font-semibold">{item.label}</div>
                      <div className="mt-1 text-xs text-slate-500">{item.detail}</div>
                    </button>
                  ))}
                </div>
              </div>
              <textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} />
              <button className="inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white">
                <MessageSquareText className="h-4 w-4" /> Ask demo workspace
              </button>
              {result ? <button className="ml-2 rounded-md border border-slate-300 px-4 py-2 text-sm" onClick={() => setResult(null)} type="button">Clear answer</button> : null}
            </form>
            {result ? (
              <div className="mt-4 space-y-3">
                <pre className="whitespace-pre-wrap rounded-md bg-teal-50 p-3 text-sm text-teal-950">{result.answer}</pre>
                <div className="rounded-md border border-slate-200 p-3 text-sm">
                  <b>Citations</b>
                  <div className="mt-2 grid gap-2">
                    {result.citations.length ? result.citations.map((citation) => (
                      <div key={citation.id} className="flex flex-wrap gap-2">
                        <Badge tone="accent">[{citation.id}]</Badge>
                        <span>{citation.filename}</span>
                        <Badge>{citation.classification}</Badge>
                      </div>
                    )) : <span className="text-slate-500">No authorized citations were used.</span>}
                  </div>
                </div>
              </div>
            ) : null}
          </section>
        </div>

        <section className="mt-5 grid gap-3 md:grid-cols-3">
          {demoDocs.map((doc) => {
            const allowed = doc.roles.includes(role);
            return (
              <article key={doc.filename} className={`rounded-lg border bg-white p-4 shadow-sm ${allowed ? "border-slate-200" : "border-red-200"}`}>
                <div className="flex flex-wrap gap-2"><b>{doc.filename}</b><Badge tone="accent">{doc.classification}</Badge>{allowed ? <Badge tone="success">Authorized</Badge> : <Badge tone="danger">Restricted</Badge>}</div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{allowed ? doc.lines[0] : "This role cannot retrieve this document."}</p>
              </article>
            );
          })}
        </section>
      </div>
    </main>
  );
}

function extractQuestions(query: string) {
  const matches = [...query.matchAll(/(?:^|\n|\s)(?:\d+[\).]\s*)?([^?\n]+[?])/g)].map((match) => match[1].trim());
  return matches.length ? matches : [query.trim()].filter(Boolean);
}

function findEvidence(question: string, docs: typeof demoDocs) {
  const q = question.toLowerCase();
  for (const doc of docs) {
    const line = doc.lines.find((item) => {
      const lower = item.toLowerCase();
      return (q.includes("vpn") && lower.includes("vpn access"))
        || (q.includes("password") && lower.includes("passwords must"))
        || (q.includes("review") && lower.includes("review"))
        || (q.includes("classification") && lower.includes("document classification"))
        || (q.includes("payroll") && lower.includes("payroll exports"))
        || (q.includes("contractor") && lower.includes("contractors"));
    });
    if (line) return { filename: doc.filename, classification: doc.classification, line };
  }
  return null;
}
