"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Archive,
  BarChart3,
  Download,
  Edit3,
  FileText,
  Gauge,
  LockKeyhole,
  LogOut,
  MessageSquareText,
  RefreshCw,
  RotateCcw,
  Search,
  Trash2,
  X,
  UploadCloud
} from "lucide-react";
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
  can_edit: boolean;
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
    metadata?: { document?: { classification?: string; uploaded_by?: string } };
    retrieval_score: number;
    rerank_score: number;
  }>;
  hallucination: { score: number; confidence: string; unsupported_claims: string[] };
  retrieval: Record<string, number | string[]>;
};

type EventRow = { time: string; action: string; result: string; detail: string };
type Toast = { id: number; tone: "success" | "error" | "info"; message: string };

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const roleOptions = ["viewer", "employee", "manager", "tenant_admin"];
const classificationOptions = ["Public", "Internal", "Confidential", "Restricted"];

export function WorkspaceApp() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [claims, setClaims] = useState<SessionClaims | null>(null);
  const [active, setActive] = useState("home");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [allowedRoles, setAllowedRoles] = useState(["viewer", "tenant_admin"]);
  const [classification, setClassification] = useState("Internal");
  const [query, setQuery] = useState("");
  const [chat, setChat] = useState<ChatResult | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [events, setEvents] = useState<EventRow[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [editingDocumentId, setEditingDocumentId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [documentsLoading, setDocumentsLoading] = useState(false);

  const admin = isTenantAdmin(claims);
  const canUpload = admin;
  const primaryRole = admin ? "tenant_admin" : claims?.roles[0] ?? "viewer";
  const nav = admin ? ["home", "documents", "ask", "settings"] : ["home", "documents", "ask"];

  useEffect(() => {
    const stored = getStoredToken();
    const parsed = stored ? readClaims(stored) : null;
    if (!stored || !parsed) {
      router.replace("/login");
      return;
    }
    setToken(stored);
    setClaims(parsed);
    hydrateClaims(stored, parsed);
    loadDocuments(stored);
    loadActivity(stored);
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

  function notify(message: string, tone: Toast["tone"] = "info") {
    const id = Date.now();
    setToasts((current) => [{ id, tone, message }, ...current].slice(0, 4));
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 4500);
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
    setDocumentsLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/v1/documents`, { headers: { Authorization: `Bearer ${authToken}` } });
      const body = await response.json();
      if (response.ok) setDocuments(body.payload.documents);
    } finally {
      setDocumentsLoading(false);
    }
  }

  async function hydrateClaims(authToken: string, fallback: SessionClaims) {
    const response = await fetch(`${apiBase}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${authToken}` } });
    const body = await response.json();
    if (response.ok) {
      setClaims({
        subject: fallback.subject,
        email: fallback.email,
        tenant: body.payload.tenant_id,
        roles: body.payload.roles
      });
    }
  }

  async function loadActivity(authToken = token) {
    if (!authToken) return;
    const response = await fetch(`${apiBase}/api/v1/activity`, { headers: { Authorization: `Bearer ${authToken}` } });
    const body = await response.json();
    if (response.ok) {
      setEvents(body.payload.events.map((event: { created_at: string; event_type: string; resource_type?: string; resource_id?: string }) => ({
        time: new Date(event.created_at).toLocaleString(),
        action: event.event_type,
        result: event.resource_type ?? "workspace",
        detail: event.resource_id ?? ""
      })));
    }
  }

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!canUpload) {
      notify("Your current role cannot upload documents.", "error");
      return;
    }
    if (!file) {
      notify("Choose a file first.", "error");
      return;
    }
    const data = new FormData();
    data.append("file", file);
    data.append("allowed_roles", allowedRoles.join(","));
    data.append("classification", classification);
    data.append("pii_sensitive", classification === "Restricted" ? "true" : "false");
    setUploading(true);
    try {
      const response = await api("/api/v1/documents/upload", { method: "POST", body: data });
      const body = await response.json();
      if (!response.ok) {
        notify(body.error?.message ?? body.detail ?? "Upload failed.", "error");
        addEvent("Upload", "Failed", file.name);
        return;
      }
      notify(`${body.payload.title} indexed successfully with ${body.payload.chunk_count} chunk(s).`, "success");
      addEvent("Upload", "Indexed", `${body.payload.title} - ${classification}`);
      setFile(null);
      const input = window.document.querySelector<HTMLInputElement>('input[type="file"]');
      if (input) input.value = "";
      await loadDocuments();
      await loadActivity();
    } catch {
      notify("Upload failed because the API could not be reached. Check that the backend is running on port 8000.", "error");
      addEvent("Upload", "Failed", file.name);
    } finally {
      setUploading(false);
    }
  }

  async function ask(event?: FormEvent, override?: string) {
    event?.preventDefault();
    const prompt = override ?? query;
    if (!prompt.trim()) return;
    notify("Searching authorized documents with governed retrieval...", "info");
    const response = await api("/api/v1/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: prompt, stream: false })
    });
    const body = await response.json();
    if (!response.ok) {
      notify(body.error?.message ?? "Query failed.", "error");
      addEvent("Query", "Failed", prompt);
      return;
    }
    setChat(body.payload);
    setQuery(prompt);
    notify("Answer generated from authorized evidence.", "success");
    addEvent("Query", "Completed", prompt);
    await loadActivity();
  }

  async function lifecycle(document: DocumentRecord, action: "archive" | "restore" | "delete" | "permanent") {
    if (!admin && !document.can_edit) return;
    if ((action === "delete" || action === "permanent") && !window.confirm(`Confirm ${action} for ${document.title}?`)) return;
    const path = action === "delete"
      ? `/api/v1/documents/${document.document_id}`
      : `/api/v1/documents/${document.document_id}/${action === "permanent" ? "permanent" : action}`;
    const response = await api(path, { method: action === "archive" || action === "restore" ? "POST" : "DELETE" });
    if (!response.ok) {
      notify(`${action} failed.`, "error");
      return;
    }
    notify(`${document.title} ${action} completed.`, "success");
    addEvent("Lifecycle", action, document.title);
    await loadDocuments();
    await loadActivity();
  }

  async function download(document: DocumentRecord) {
    const response = await api(`/api/v1/documents/${document.document_id}/download`);
    if (!response.ok) {
      notify("Download unavailable for this document.", "error");
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

  async function updateDocument(document: DocumentRecord, nextClassification: string, nextRoles: string[]) {
    if (!admin && !document.can_edit) return;
    if (!nextRoles.length) {
      notify("Select at least one allowed role for this document.", "error");
      return;
    }
    const response = await api(`/api/v1/documents/${document.document_id}/metadata`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        classification: nextClassification,
        allowed_roles: nextRoles,
        description: "",
        tags: []
      })
    });
    const body = await response.json();
    if (!response.ok) {
      notify(body.error?.message ?? body.detail ?? "Document update failed.", "error");
      return;
    }
    notify(`${document.title} access settings updated.`, "success");
    setEditingDocumentId(null);
    addEvent("Metadata", "Updated", document.title);
    await loadDocuments();
    await loadActivity();
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
              <Badge tone="success">Organization</Badge>
              <Badge tone="accent">{claims.tenant}</Badge>
              <Badge tone={admin ? "success" : "neutral"}>{primaryRole}</Badge>
            </div>
            <h1 className="mt-2 text-2xl font-semibold tracking-normal">Knowledge Governance Workspace</h1>
          </div>
          <div className="flex flex-wrap gap-2">
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
            <div className="mt-1 text-xs text-slate-500">{primaryRole}</div>
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
          {active === "home" && <Dashboard summary={summary} claims={claims} />}
          {active === "ask" && <AskView query={query} setQuery={setQuery} ask={ask} chat={chat} clearChat={() => setChat(null)} />}
          {active === "documents" && (
            <DocumentsView
              admin={admin}
              canUpload={canUpload}
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
              updateDocument={updateDocument}
              editingDocumentId={editingDocumentId}
              setEditingDocumentId={setEditingDocumentId}
              uploading={uploading}
              documentsLoading={documentsLoading}
              reload={() => loadDocuments()}
            />
          )}
          {active === "settings" && admin && <AdminView claims={claims} summary={summary} documents={documents} events={events} />}
        </section>
      </div>
      <ToastStack toasts={toasts} dismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))} />
    </main>
  );
}

function Dashboard({ summary, claims }: { summary: { documents: number; chunks: number; restricted: number; archived: number }; claims: SessionClaims }) {
  const admin = isTenantAdmin(claims);
  return (
    <div className="space-y-4">
      {admin ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric icon={<FileText />} label="Documents" value={summary.documents} />
          <Metric icon={<BarChart3 />} label="Indexed chunks" value={summary.chunks} />
          <Metric icon={<LockKeyhole />} label="Role-restricted" value={summary.restricted} />
          <Metric icon={<Archive />} label="Archived" value={summary.archived} />
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <Metric icon={<FileText />} label="Authorized documents" value={summary.documents} />
          <Metric icon={<BarChart3 />} label="Searchable chunks" value={summary.chunks} />
          <Metric icon={<LockKeyhole />} label="Your role" value={claims.roles[0] ?? "viewer"} />
        </div>
      )}
      <Card title="What this workspace does">
        <div className="grid gap-3 text-sm text-slate-600 md:grid-cols-3">
          {admin ? <div>Tenant admins upload files, classify them, and assign allowed retrieval roles.</div> : <div>Your role can ask questions only against documents approved for your access.</div>}
          <div>Unauthorized documents are filtered before retrieval and answer generation.</div>
          <div>Answers show citations, grounding quality, and retrieval diagnostics.</div>
        </div>
      </Card>
      <Card title="Current access scope">
        <div className="text-sm text-slate-600">Signed in as <b>{claims.subject}</b> with roles <b>{claims.roles.join(", ")}</b>.</div>
      </Card>
    </div>
  );
}

function DocumentsView(props: {
  admin: boolean; canUpload: boolean; file: File | null; setFile: (file: File | null) => void; classification: string; setClassification: (value: string) => void; allowedRoles: string[]; toggleRole: (role: string) => void; upload: (event: FormEvent) => void; documents: DocumentRecord[]; search: string; setSearch: (value: string) => void; filter: string; setFilter: (value: string) => void; lifecycle: (document: DocumentRecord, action: "archive" | "restore" | "delete" | "permanent") => void; download: (document: DocumentRecord) => void; updateDocument: (document: DocumentRecord, classification: string, allowedRoles: string[]) => void; editingDocumentId: string | null; setEditingDocumentId: (documentId: string | null) => void; uploading: boolean; documentsLoading: boolean; reload: () => void;
}) {
  return (
    <div className="space-y-4">
      {props.canUpload ? (
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
            <button disabled={props.uploading} className="inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-70">
              {props.uploading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              {props.uploading ? "Uploading..." : "Upload and index"}
            </button>
          </form>
        </Card>
      ) : (
        <Card title="Repository access">
          <p className="text-sm text-slate-600">Your role can browse approved documents and ask questions. Upload and management controls are hidden.</p>
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
          <button disabled={props.documentsLoading} className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-70" onClick={props.reload} type="button"><RefreshCw className={`h-4 w-4 ${props.documentsLoading ? "animate-spin" : ""}`} /> Refresh</button>
        </div>
        <div className="grid gap-3">
          {props.documentsLoading && (
            <div className="grid gap-3">
              {[0, 1, 2].map((item) => <div key={item} className="h-20 animate-pulse rounded-lg bg-slate-100" />)}
            </div>
          )}
          {!props.documentsLoading && props.documents.map((document) => (
            <div key={document.document_id} className="rounded-lg border border-slate-200 p-3">
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="font-medium">{document.title}</div>
                  <div className="mt-1 text-xs text-slate-500">{document.chunk_count} chunks - {document.allowed_roles.join(", ")} - uploaded {new Date(document.created_at).toLocaleDateString()}</div>
                  <div className="mt-2 flex flex-wrap gap-2"><Badge tone="accent">{document.classification}</Badge><Badge tone={document.state === "Active" ? "success" : "neutral"}>{document.state}</Badge></div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <IconButton title="Download original" onClick={() => props.download(document)}><Download className="h-4 w-4" /></IconButton>
                  {(props.admin || document.can_edit) && <IconButton title="Edit access" onClick={() => props.setEditingDocumentId(props.editingDocumentId === document.document_id ? null : document.document_id)}><Edit3 className="h-4 w-4" /></IconButton>}
                  {(props.admin || document.can_edit) && document.state === "Active" && <IconButton title="Archive" onClick={() => props.lifecycle(document, "archive")}><Archive className="h-4 w-4" /></IconButton>}
                  {(props.admin || document.can_edit) && document.state !== "Active" && <IconButton title="Restore" onClick={() => props.lifecycle(document, "restore")}><RotateCcw className="h-4 w-4" /></IconButton>}
                  {(props.admin || document.can_edit) && document.state !== "Deleted" && <IconButton title="Soft delete" onClick={() => props.lifecycle(document, "delete")} danger><Trash2 className="h-4 w-4" /></IconButton>}
                  {(props.admin || document.can_edit) && document.state === "Deleted" && <IconButton title="Permanently delete" onClick={() => props.lifecycle(document, "permanent")} danger><Trash2 className="h-4 w-4" /></IconButton>}
                </div>
              </div>
              {(props.admin || document.can_edit) && props.editingDocumentId === document.document_id && (
                <DocumentAccessEditor document={document} updateDocument={props.updateDocument} />
              )}
            </div>
          ))}
          {!props.documentsLoading && !props.documents.length && <div className="rounded-md border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">No documents match this view.</div>}
        </div>
      </Card>
    </div>
  );
}

function DocumentAccessEditor({
  document,
  updateDocument
}: {
  document: DocumentRecord;
  updateDocument: (document: DocumentRecord, classification: string, allowedRoles: string[]) => void;
}) {
  const [classification, setClassification] = useState(document.classification);
  const [roles, setRoles] = useState(document.allowed_roles);
  const dirty = classification !== document.classification || roles.slice().sort().join(",") !== document.allowed_roles.slice().sort().join(",");

  useEffect(() => {
    setClassification(document.classification);
    setRoles(document.allowed_roles);
  }, [document.classification, document.allowed_roles]);

  function toggle(role: string) {
    setRoles((current) => current.includes(role) ? current.filter((item) => item !== role) : [...current, role]);
  }

  return (
    <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3">
      <div className="grid gap-3 lg:grid-cols-[180px_1fr_auto] lg:items-start">
        <select className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm" value={classification} onChange={(event) => setClassification(event.target.value)}>
          {classificationOptions.map((item) => <option key={item}>{item}</option>)}
        </select>
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          {roleOptions.map((role) => (
            <button type="button" key={role} onClick={() => toggle(role)} className={`rounded-md border bg-white px-3 py-2 text-left text-xs ${roles.includes(role) ? "border-teal-300 text-teal-800" : "border-slate-200 text-slate-500"}`}>
              {role}
            </button>
          ))}
        </div>
        <button disabled={!dirty || roles.length === 0} className="rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50" onClick={() => updateDocument(document, classification, roles)} type="button">
          Save access
        </button>
      </div>
    </div>
  );
}

function AskView({ query, setQuery, ask, chat, clearChat }: { query: string; setQuery: (value: string) => void; ask: (event?: FormEvent, override?: string) => void; chat: ChatResult | null; clearChat: () => void }) {
  return (
    <div className="space-y-4">
      <Card title="Ask AI">
        <form className="space-y-3" onSubmit={ask}>
          <textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask one or more questions about documents you are authorized to access." />
          <div className="flex flex-wrap gap-2">
            <button className="inline-flex items-center gap-2 rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white">
              <MessageSquareText className="h-4 w-4" /> Ask with governed retrieval
            </button>
            {chat && <button className="rounded-md border border-slate-300 px-4 py-2 text-sm" onClick={clearChat} type="button">Clear answer</button>}
          </div>
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
              <div className="mt-2 text-xs text-slate-500">Classification: {citation.metadata?.document?.classification ?? "Unknown"}</div>
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

function AdminView({ claims, summary, documents, events }: { claims: SessionClaims; summary: { documents: number; chunks: number; restricted: number; archived: number }; documents: DocumentRecord[]; events: EventRow[] }) {
  return (
    <div className="space-y-4">
      <Card title="Organization administration">
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-md border border-slate-200 p-3 text-sm">Tenant: {claims.tenant}</div>
          <div className="rounded-md border border-slate-200 p-3 text-sm">Current admin: {claims.subject}</div>
        </div>
      </Card>
      <ActivityView events={events} />
      <Card title="Governance report">
        <pre className="overflow-auto rounded-md bg-slate-50 p-3 text-xs">{JSON.stringify({ tenant: claims.tenant, summary, documents: documents.map(({ title, classification, allowed_roles, state }) => ({ title, classification, allowed_roles, state })) }, null, 2)}</pre>
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

function ToastStack({ toasts, dismiss }: { toasts: Toast[]; dismiss: (id: number) => void }) {
  return (
    <div className="fixed right-4 top-4 z-50 grid w-[calc(100%-2rem)] max-w-sm gap-2">
      {toasts.map((toast) => (
        <div key={toast.id} className={`flex items-start justify-between gap-3 rounded-lg border bg-white p-3 text-sm shadow-lg ${toast.tone === "success" ? "border-teal-200 text-teal-900" : toast.tone === "error" ? "border-red-200 text-red-800" : "border-slate-200 text-slate-700"}`}>
          <span>{toast.message}</span>
          <button type="button" title="Dismiss" onClick={() => dismiss(toast.id)}><X className="h-4 w-4" /></button>
        </div>
      ))}
    </div>
  );
}
