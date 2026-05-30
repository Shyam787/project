"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Archive,
  BarChart3,
  Download,
  FileText,
  Gauge,
  LockKeyhole,
  LogOut,
  MessageSquareText,
  RefreshCw,
  RotateCcw,
  Search,
  Trash2,
  UploadCloud
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui";
import { clearSession, getStoredToken, isTenantAdmin, readClaims } from "@/components/auth";
import type { SessionClaims } from "@/components/auth";

type DocumentRecord = {
  document_id: string;
  title: string;
  status: string;
  state: string;
  uploaded_by: string;
  classification: string;
  allowed_roles: string[];
  chunk_count: number;
  storage_path: string;
  created_at: string;
};

type ChatResult = {
  answer: string;
  citations: Array<{
    citation_id: string;
    document_id: string;
    chunk_id: string;
    source_location?: { filename?: string };
    retrieval_score: number;
    rerank_score: number;
  }>;
  hallucination: { score: number; confidence: string; unsupported_claims: string[] };
  retrieval: Record<string, number | string[]>;
};

type EventRow = { time: string; action: string; result: string; detail: string };

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const roleOptions = ["viewer", "employee", "manager", "tenant_admin"];
const classificationOptions = ["Public", "Internal", "Confidential", "Restricted"];

export function WorkspaceApp() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [claims, setClaims] = useState<SessionClaims | null>(null);
  const [active, setActive] = useState("ask");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [allowedRoles, setAllowedRoles] = useState(["viewer", "tenant_admin"]);
  const [classification, setClassification] = useState("Internal");
  const [query, setQuery] = useState("1. Who gets VPN access? 2. What are password requirements? 3. What is the document classification?");
  const [chat, setChat] = useState<ChatResult | null>(null);
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [events, setEvents] = useState<EventRow[]>([]);

  const admin = isTenantAdmin(claims);
  const nav = admin ? ["dashboard", "ask", "documents", "activity", "evaluation", "admin"] : ["dashboard", "ask", "documents", "activity", "evaluation"];

  useEffect(() => {
    const stored = getStoredToken();
    const parsed = stored ? readClaims(stored) : null;
    if (!stored || !parsed) {
      router.replace("/login");
      return;
    }
    setToken(stored);
    setClaims(parsed);
    loadDocuments(stored);
  }, [router]);

  const visibleDocs = useMemo(() => {
    return documents.filter((document) => {
      const haystack = `${document.title} ${document.classification} ${document.allowed_roles.join(" ")} ${document.state}`.toLowerCase();
      const matchesSearch = haystack.includes(search.toLowerCase());
      const matchesFilter = filter === "All" || document.classification === filter || document.state === filter;
      return matchesSearch && matchesFilter;
    });
  }, [documents, filter, search]);

  const summary = useMemo(() => ({
    documents: documents.length,
    chunks: documents.reduce((sum, document) => sum + document.chunk_count, 0),
    restricted: documents.filter((document) => !document.allowed_roles.includes("viewer")).length,
    archived: documents.filter((document) => document.state === "Archived").length
  }), [documents]);

  function addEvent(action: string, result: string, detail: string) {
    setEvents((current) => [{ time: new Date().toLocaleTimeString(), action, result, detail }, ...current].slice(0, 10));
  }

  async function api(path: string, init: RequestInit = {}) {
    return fetch(`${apiBase}${path}`, {
      ...init,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(init.headers ?? {})
      }
    });
  }

  async function loadDocuments(authToken = token) {
    if (!authToken) return;
    const response = await fetch(`${apiBase}/api/v1/documents`, { headers: { Authorization: `Bearer ${authToken}` } });
    const body = await response.json();
    if (response.ok) setDocuments(body.payload.documents);
  }

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!admin) {
      setStatus("Your current role cannot upload documents.");
      return;
    }
    if (!file) {
      setStatus("Choose a file first.");
      return;
    }
    const data = new FormData();
    data.append("file", file);
    data.append("allowed_roles", allowedRoles.join(","));
    data.append("classification", classification);
    data.append("pii_sensitive", classification === "Restricted" ? "true" : "false");
    setStatus("Uploading, extracting, chunking, embedding, and indexing...");
    try {
      const response = await api("/api/v1/documents/upload", { method: "POST", body: data });
      const body = await response.json();
      if (!response.ok) {
        setStatus(body.error?.message ?? body.detail ?? "Upload failed.");
        addEvent("Upload", "Failed", file.name);
        return;
      }
      setStatus(`${body.payload.title} indexed successfully with ${body.payload.chunk_count} chunk(s).`);
      addEvent("Upload", "Indexed", `${body.payload.title} - ${classification}`);
      setFile(null);
      const input = window.document.querySelector<HTMLInputElement>('input[type="file"]');
      if (input) input.value = "";
      await loadDocuments();
    } catch {
      setStatus("Upload failed because the API could not be reached. Check that the backend is running on port 8000.");
      addEvent("Upload", "Failed", file.name);
    }
  }

  async function ask(event?: FormEvent, override?: string) {
    event?.preventDefault();
    const prompt = override ?? query;
    if (!prompt.trim()) return;
    setStatus("RBAC filtering authorized documents before hybrid retrieval...");
    const response = await api("/api/v1/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: prompt, stream: false })
    });
    const body = await response.json();
    if (!response.ok) {
      setStatus(body.error?.message ?? "Query failed.");
      addEvent("Query", "Failed", prompt);
      return;
    }
    setChat(body.payload);
    setQuery(prompt);
    setStatus("Answer generated from authorized evidence.");
    addEvent("Query", "Completed", prompt);
  }

  async function lifecycle(document: DocumentRecord, action: "archive" | "restore" | "delete" | "permanent") {
    if (!admin) return;
    if ((action === "delete" || action === "permanent") && !window.confirm(`Confirm ${action} for ${document.title}?`)) return;
    const path = action === "delete"
      ? `/api/v1/documents/${document.document_id}`
      : `/api/v1/documents/${document.document_id}/${action === "permanent" ? "permanent" : action}`;
    const response = await api(path, { method: action === "archive" || action === "restore" ? "POST" : "DELETE" });
    if (!response.ok) {
      setStatus(`${action} failed.`);
      return;
    }
    addEvent("Lifecycle", action, document.title);
    await loadDocuments();
  }

  async function download(document: DocumentRecord) {
    const response = await api(`/api/v1/documents/${document.document_id}/download`);
    if (!response.ok) {
      setStatus("Download unavailable for this document.");
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = document.title;
    link.click();
    URL.revokeObjectURL(url);
  }

  function logout() {
    clearSession();
    router.replace("/login");
  }

  function toggleRole(role: string) {
    setAllowedRoles((roles) => roles.includes(role) ? roles.filter((item) => item !== role) : [...roles, role]);
  }

  if (!claims) return <main className="min-h-screen bg-slate-50 p-6 text-sm">Loading secure workspace...</main>;

  return (
    <main className="min-h-screen bg-[#f7f8fb]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex flex-wrap gap-2">
              <Badge tone="success">ACME Corporation</Badge>
              <Badge tone="accent">{claims.tenant}</Badge>
              <Badge tone={admin ? "success" : "neutral"}>{admin ? "Tenant Admin" : "Viewer"}</Badge>
            </div>
            <h1 className="mt-2 text-2xl font-semibold tracking-normal">Knowledge Governance Workspace</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link className="rounded-md border border-slate-300 px-3 py-2 text-sm" href="/">Landing</Link>
            <button className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={logout}>
              <LogOut className="h-4 w-4" /> Logout
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-4 px-4 py-5 sm:px-6 lg:grid-cols-[230px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-white p-3 lg:sticky lg:top-4 lg:h-fit">
          <div className="mb-3 rounded-md bg-slate-50 p-3 text-sm">
            <div className="font-medium">{claims.subject}</div>
            <div className="mt-1 text-xs text-slate-500">{claims.roles.join(", ")}</div>
          </div>
          <nav className="grid gap-1">
            {nav.map((item) => (
              <button key={item} className={`rounded-md px-3 py-2 text-left text-sm capitalize ${active === item ? "bg-teal-50 text-teal-800" : "hover:bg-slate-50"}`} onClick={() => setActive(item)}>
                {item}
              </button>
            ))}
          </nav>
        </aside>

        <section className="space-y-4">
          {active === "dashboard" && <Dashboard summary={summary} claims={claims} />}
          {active === "ask" && <AskView query={query} setQuery={setQuery} ask={ask} chat={chat} />}
          {active === "documents" && (
            <DocumentsView
              admin={admin}
              file={file}
              setFile={setFile}
              classification={classification}
              setClassification={setClassification}
              allowedRoles={allowedRoles}
              toggleRole={toggleRole}
              upload={upload}
              documents={visibleDocs}
              search={search}
              setSearch={setSearch}
              filter={filter}
              setFilter={setFilter}
              lifecycle={lifecycle}
              download={download}
              reload={() => loadDocuments()}
            />
          )}
          {active === "activity" && <ActivityView events={events} />}
          {active === "evaluation" && <EvaluationView ask={ask} />}
          {active === "admin" && admin && <AdminView claims={claims} summary={summary} documents={documents} />}
          {status && <div className="rounded-md border border-slate-200 bg-white p-3 text-sm text-slate-600">{status}</div>}
        </section>
      </div>
    </main>
  );
}

function Dashboard({ summary, claims }: { summary: { documents: number; chunks: number; restricted: number; archived: number }; claims: SessionClaims }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<FileText />} label="Documents" value={summary.documents} />
        <Metric icon={<BarChart3 />} label="Indexed chunks" value={summary.chunks} />
        <Metric icon={<LockKeyhole />} label="Restricted" value={summary.restricted} />
        <Metric icon={<Archive />} label="Archived" value={summary.archived} />
      </div>
      <Card title="What this workspace does">
        <div className="grid gap-3 text-sm text-slate-600 md:grid-cols-3">
          <div>Admins upload files and assign allowed roles.</div>
          <div>Users ask questions only against authorized documents.</div>
          <div>Answers show citations, grounding quality, and diagnostics.</div>
        </div>
      </Card>
      <Card title="Current access scope">
        <div className="text-sm text-slate-600">Signed in as <b>{claims.subject}</b> with roles <b>{claims.roles.join(", ")}</b>.</div>
      </Card>
    </div>
  );
}

function DocumentsView(props: {
  admin: boolean; file: File | null; setFile: (file: File | null) => void; classification: string; setClassification: (value: string) => void; allowedRoles: string[]; toggleRole: (role: string) => void; upload: (event: FormEvent) => void; documents: DocumentRecord[]; search: string; setSearch: (value: string) => void; filter: string; setFilter: (value: string) => void; lifecycle: (document: DocumentRecord, action: "archive" | "restore" | "delete" | "permanent") => void; download: (document: DocumentRecord) => void; reload: () => void;
}) {
  return (
    <div className="space-y-4">
      {props.admin ? (
        <Card title="Upload document">
          <form className="space-y-4" onSubmit={props.upload}>
            <div className="grid gap-3 lg:grid-cols-[180px_1fr]">
              <select className="rounded-md border border-slate-300 px-3 py-2 text-sm" value={props.classification} onChange={(event) => props.setClassification(event.target.value)}>
                {classificationOptions.map((item) => <option key={item}>{item}</option>)}
              </select>
              <input className="rounded-md border border-slate-300 px-3 py-2 text-sm" type="file" accept=".txt,.md,.pdf,.docx" onChange={(event) => props.setFile(event.target.files?.[0] ?? null)} />
            </div>
            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
              {roleOptions.map((role) => (
                <button type="button" key={role} onClick={() => props.toggleRole(role)} className={`rounded-md border p-3 text-left text-sm ${props.allowedRoles.includes(role) ? "border-teal-300 bg-teal-50" : "border-slate-200 bg-white"}`}>
                  <div className="font-medium">{role}</div>
                  <div className="text-xs text-slate-500">Allowed to retrieve</div>
                </button>
              ))}
            </div>
            <button className="inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white">
              <UploadCloud className="h-4 w-4" /> Upload and index
            </button>
          </form>
        </Card>
      ) : (
        <Card title="Repository access">
          <p className="text-sm text-slate-600">Your viewer role can browse approved documents and ask questions. Upload and delete controls are hidden.</p>
        </Card>
      )}

      <Card title="Document repository">
        <div className="mb-3 grid gap-2 md:grid-cols-[1fr_170px_auto]">
          <div className="flex items-center gap-2 rounded-md border border-slate-300 px-3">
            <Search className="h-4 w-4 text-slate-500" />
            <input className="min-w-0 flex-1 py-2 text-sm outline-none" value={props.search} onChange={(event) => props.setSearch(event.target.value)} placeholder="Search repository" />
          </div>
          <select className="rounded-md border border-slate-300 px-3 py-2 text-sm" value={props.filter} onChange={(event) => props.setFilter(event.target.value)}>
            {["All", ...classificationOptions, "Active", "Archived", "Deleted"].map((item) => <option key={item}>{item}</option>)}
          </select>
          <button className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={props.reload} type="button"><RefreshCw className="h-4 w-4" /> Refresh</button>
        </div>
        <div className="grid gap-3">
          {props.documents.map((document) => (
            <div key={document.document_id} className="rounded-lg border border-slate-200 p-3">
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="font-medium">{document.title}</div>
                  <div className="mt-1 text-xs text-slate-500">{document.chunk_count} chunks - {document.allowed_roles.join(", ")} - uploaded {new Date(document.created_at).toLocaleDateString()}</div>
                  <div className="mt-2 flex flex-wrap gap-2"><Badge tone="accent">{document.classification}</Badge><Badge tone={document.state === "Active" ? "success" : "neutral"}>{document.state}</Badge></div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <IconButton title="Download original" onClick={() => props.download(document)}><Download className="h-4 w-4" /></IconButton>
                  {props.admin && document.state === "Active" && <IconButton title="Archive" onClick={() => props.lifecycle(document, "archive")}><Archive className="h-4 w-4" /></IconButton>}
                  {props.admin && document.state !== "Active" && <IconButton title="Restore" onClick={() => props.lifecycle(document, "restore")}><RotateCcw className="h-4 w-4" /></IconButton>}
                  {props.admin && document.state !== "Deleted" && <IconButton title="Soft delete" onClick={() => props.lifecycle(document, "delete")} danger><Trash2 className="h-4 w-4" /></IconButton>}
                  {props.admin && document.state === "Deleted" && <IconButton title="Permanently delete" onClick={() => props.lifecycle(document, "permanent")} danger><Trash2 className="h-4 w-4" /></IconButton>}
                </div>
              </div>
            </div>
          ))}
          {!props.documents.length && <div className="rounded-md border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">No documents match this view.</div>}
        </div>
      </Card>
    </div>
  );
}

function AskView({ query, setQuery, ask, chat }: { query: string; setQuery: (value: string) => void; ask: (event?: FormEvent, override?: string) => void; chat: ChatResult | null }) {
  return (
    <div className="space-y-4">
      <Card title="Ask AI">
        <form className="space-y-3" onSubmit={ask}>
          <textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} />
          <button className="inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white">
            <MessageSquareText className="h-4 w-4" /> Ask with governed retrieval
          </button>
        </form>
      </Card>
      {chat && <Answer chat={chat} />}
    </div>
  );
}

function Answer({ chat }: { chat: ChatResult }) {
  return (
    <div className="space-y-4">
      <Card title="Grounded answer">
        <div className="mb-3 flex flex-wrap gap-2">
          <Badge tone={chat.hallucination.score === 0 ? "success" : "danger"}>Grounding: {chat.hallucination.confidence}</Badge>
          <Badge tone="accent">Citations validated</Badge>
        </div>
        <pre className="whitespace-pre-wrap rounded-md bg-teal-50 p-3 text-sm text-teal-950">{chat.answer}</pre>
      </Card>
      <Card title="Why this answer was generated">
        <div className="grid gap-3">
          {chat.citations.map((citation) => (
            <div className="rounded-md border border-slate-200 p-3 text-sm" key={citation.citation_id}>
              <div className="flex flex-wrap gap-2"><Badge tone="accent">[{citation.citation_id}]</Badge><b>{citation.source_location?.filename ?? citation.document_id}</b><Badge>{citation.rerank_score >= 0.4 ? "High match" : "Match"}</Badge></div>
              <div className="mt-2 text-xs text-slate-500">Document: {citation.document_id}</div>
            </div>
          ))}
        </div>
      </Card>
      <Card title="Advanced diagnostics">
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(chat.retrieval).map(([key, value]) => <Metric key={key} icon={<Gauge />} label={key.replaceAll("_", " ")} value={Array.isArray(value) ? value.length : value} />)}
        </div>
      </Card>
    </div>
  );
}

function ActivityView({ events }: { events: EventRow[] }) {
  return <Card title="Workspace activity">{events.length ? events.map((event) => <div key={`${event.time}-${event.action}`} className="border-b border-slate-100 py-3 text-sm"><b>{event.action}</b> - {event.result}<div className="text-xs text-slate-500">{event.time} - {event.detail}</div></div>) : <p className="text-sm text-slate-500">Activity appears here after uploads, queries, and lifecycle actions.</p>}</Card>;
}

function EvaluationView({ ask }: { ask: (event?: FormEvent, override?: string) => void }) {
  const tests = [
    ["Viewer RBAC denial", "Who approves purchases above 25000 USD?"],
    ["Multi-question policy extraction", "1. Who gets VPN access? 2. What are password requirements? 3. What is the document classification?"],
    ["Unsupported question", "What is ACME's moon base policy?"]
  ];
  return <Card title="Evaluation center"><div className="grid gap-3">{tests.map(([name, prompt]) => <button key={name} onClick={() => ask(undefined, prompt)} className="rounded-md border border-slate-200 p-3 text-left text-sm hover:border-teal-300"><b>{name}</b><div className="mt-1 text-xs text-slate-500">{prompt}</div></button>)}</div></Card>;
}

function AdminView({ claims, summary, documents }: { claims: SessionClaims; summary: { documents: number; chunks: number; restricted: number; archived: number }; documents: DocumentRecord[] }) {
  return (
    <div className="space-y-4">
      <Card title="Organization administration">
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-md border border-slate-200 p-3 text-sm">Users: demo-admin, demo-viewer</div>
          <div className="rounded-md border border-slate-200 p-3 text-sm">Current admin: {claims.subject}</div>
        </div>
      </Card>
      <Card title="Governance report">
        <pre className="overflow-auto rounded-md bg-slate-50 p-3 text-xs">{JSON.stringify({ organization: "ACME Corporation", summary, documents: documents.map(({ title, classification, allowed_roles, state }) => ({ title, classification, allowed_roles, state })) }, null, 2)}</pre>
      </Card>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><h2 className="mb-3 text-sm font-semibold">{title}</h2>{children}</section>;
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return <div className="rounded-lg border border-slate-200 bg-white p-3"><div className="flex items-center gap-2 text-xs text-slate-500">{icon}{label}</div><div className="mt-2 text-2xl font-semibold">{String(value)}</div></div>;
}

function IconButton({ title, onClick, children, danger = false }: { title: string; onClick: () => void; children: React.ReactNode; danger?: boolean }) {
  return <button type="button" title={title} onClick={onClick} className={`rounded-md border p-2 ${danger ? "border-red-200 text-red-700" : "border-slate-300"}`}>{children}</button>;
}
