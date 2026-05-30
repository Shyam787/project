"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Archive,
  BarChart3,
  CheckCircle2,
  Database,
  Download,
  Eye,
  FileSearch,
  FileText,
  Gauge,
  KeyRound,
  LockKeyhole,
  LogIn,
  MessageSquareText,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
  UploadCloud,
  UserRound
} from "lucide-react";
import { Badge } from "@/components/ui";

type Claims = {
  subject: string;
  tenant: string;
  roles: string[];
};

type UploadResult = {
  document_id: string;
  title: string;
  status: string;
  chunk_count: number;
  allowed_roles: string[];
  classification: string;
};

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
  updated_at: string;
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

type ActivityEvent = {
  timestamp: string;
  action: string;
  result: string;
  detail: string;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const keycloakBase = process.env.NEXT_PUBLIC_KEYCLOAK_BASE_URL ?? "http://localhost:8081";
const roleOptions = ["viewer", "employee", "manager", "tenant_admin"];
const classificationOptions = ["Public", "Internal", "Confidential", "Restricted"];
const demoUsers = {
  admin: {
    label: "Tenant Admin",
    username: "demo-admin",
    password: "DemoAdmin123!",
    scope: "Can upload, govern, archive, delete, evaluate, and query all assigned documents."
  },
  viewer: {
    label: "Viewer",
    username: "demo-viewer",
    password: "DemoViewer123!",
    scope: "Can query and inspect citations for documents explicitly visible to viewer role."
  }
};

function readClaims(token: string): Claims | null {
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

function hasAdminAccess(claims: Claims | null) {
  return Boolean(claims?.roles.includes("tenant_admin"));
}

function trustLabel(score: number) {
  if (score === 0) return "Strong";
  if (score <= 0.35) return "Partial";
  return "Weak";
}

function matchStrength(score: number) {
  if (score >= 0.45) return "High";
  if (score >= 0.2) return "Medium";
  return "Low";
}

export function LiveRagConsole() {
  const [activeSection, setActiveSection] = useState("dashboard");
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("demo-admin");
  const [password, setPassword] = useState("DemoAdmin123!");
  const [showPassword, setShowPassword] = useState(false);
  const [showToken, setShowToken] = useState(false);
  const [allowedRoles, setAllowedRoles] = useState<string[]>(["viewer", "tenant_admin"]);
  const [classification, setClassification] = useState("Internal");
  const [query, setQuery] = useState(
    "1. Who gets VPN access? 2. What are password requirements? 3. What is the document classification?"
  );
  const [file, setFile] = useState<File | null>(null);
  const [upload, setUpload] = useState<UploadResult | null>(null);
  const [chat, setChat] = useState<ChatResult | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [status, setStatus] = useState("");
  const [repositorySearch, setRepositorySearch] = useState("");
  const [repositoryFilter, setRepositoryFilter] = useState("All");
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const claims = token ? readClaims(token) : null;
  const isAdmin = hasAdminAccess(claims);
  const navigationSections = useMemo(() => {
    const sections = ["dashboard", "documents", "ask", "activity", "evaluation"];
    return isAdmin ? [...sections, "admin"] : sections;
  }, [isAdmin]);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("enterprise_rag_token");
    const savedQuery = window.localStorage.getItem("enterprise_rag_recent_query");
    if (savedToken) setToken(savedToken);
    if (savedQuery) setQuery(savedQuery);
  }, []);

  useEffect(() => {
    if (token) {
      window.localStorage.setItem("enterprise_rag_token", token);
      loadDocuments(token);
    }
  }, [token]);

  useEffect(() => {
    if (!navigationSections.includes(activeSection)) {
      setActiveSection("dashboard");
    }
  }, [activeSection, navigationSections]);

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const text = `${document.title} ${document.uploaded_by} ${document.classification} ${document.allowed_roles.join(" ")}`.toLowerCase();
      const matchesSearch = text.includes(repositorySearch.toLowerCase());
      const matchesFilter = repositoryFilter === "All" || document.classification === repositoryFilter || document.state === repositoryFilter;
      return matchesSearch && matchesFilter;
    });
  }, [documents, repositorySearch, repositoryFilter]);

  const summary = useMemo(() => {
    return {
      totalDocuments: documents.length,
      indexedChunks: documents.reduce((sum, document) => sum + document.chunk_count, 0),
      restrictedDocuments: documents.filter((document) => !document.allowed_roles.includes("viewer")).length,
      archivedDocuments: documents.filter((document) => document.state === "Archived").length
    };
  }, [documents]);

  function addActivity(action: string, result: string, detail: string) {
    setActivity((events) => [
      { timestamp: new Date().toLocaleString(), action, result, detail },
      ...events
    ].slice(0, 8));
  }

  function useDemoUser(kind: keyof typeof demoUsers) {
    const user = demoUsers[kind];
    setUsername(user.username);
    setPassword(user.password);
    setToken("");
    setChat(null);
    setStatus(`${user.label} account selected. Sign in to receive Keycloak roles.`);
  }

  async function login(event: FormEvent) {
    event.preventDefault();
    setStatus("Signing in through ACME identity provider...");
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
    if (!response.ok) {
      setStatus("Incorrect username or password. Please verify your credentials and try again.");
      addActivity("user signed in", "Denied", username);
      return;
    }
    setToken(body.access_token);
    setStatus("Session active. Roles are enforced by the backend before retrieval.");
    addActivity("user signed in", "Allowed", username);
  }

  function logout() {
    setToken("");
    setChat(null);
    setDocuments([]);
    window.localStorage.removeItem("enterprise_rag_token");
    setStatus("Signed out. Protected workspace state cleared.");
  }

  async function loadDocuments(authToken = token) {
    if (!authToken) return;
    const response = await fetch(`${apiBase}/api/v1/documents`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    const body = await response.json();
    if (response.ok) setDocuments(body.payload.documents);
  }

  async function uploadFile(event: FormEvent) {
    event.preventDefault();
    if (!file || !token) {
      setStatus("Sign in and select a document before uploading.");
      return;
    }
    const data = new FormData();
    data.append("file", file);
    data.append("allowed_roles", allowedRoles.join(","));
    data.append("classification", classification);
    data.append("pii_sensitive", classification === "Restricted" ? "true" : "false");
    setStatus("Uploading document... extracting text... chunking... indexing vectors...");
    const response = await fetch(`${apiBase}/api/v1/documents/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: data
    });
    const body = await response.json();
    if (!response.ok) {
      setStatus(body.error?.message ?? "Upload failed.");
      addActivity("document uploaded", "Failed", file.name);
      return;
    }
    setUpload(body.payload);
    setStatus("Document indexed successfully and stored in the governed repository.");
    addActivity("document uploaded", "Indexed", `${file.name} (${classification})`);
    await loadDocuments();
  }

  async function askQuestion(event?: FormEvent, overrideQuery?: string) {
    event?.preventDefault();
    const effectiveQuery = overrideQuery ?? query;
    if (!token || !effectiveQuery.trim()) {
      setStatus("Sign in and enter a question before querying.");
      return;
    }
    window.localStorage.setItem("enterprise_rag_recent_query", effectiveQuery);
    setStatus("Applying RBAC before retrieval, then running hybrid search and grounding checks...");
    const response = await fetch(`${apiBase}/api/v1/chat/query`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query: effectiveQuery, stream: false })
    });
    const body = await response.json();
    if (!response.ok) {
      setStatus(body.error?.message ?? "Query failed.");
      addActivity("query executed", "Failed", effectiveQuery);
      return;
    }
    setChat(body.payload);
    setQuery(effectiveQuery);
    setStatus("Answer generated from authorized enterprise evidence.");
    addActivity("query executed", "Grounded", effectiveQuery);
  }

  async function documentAction(documentId: string, action: "archive" | "restore" | "delete" | "permanent") {
    if (!token) return;
    const url =
      action === "delete"
        ? `${apiBase}/api/v1/documents/${documentId}`
        : `${apiBase}/api/v1/documents/${documentId}/${action === "permanent" ? "permanent" : action}`;
    const response = await fetch(url, {
      method: action === "delete" || action === "permanent" ? "DELETE" : "POST",
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) {
      setStatus("Document lifecycle action failed.");
      return;
    }
    addActivity(`document ${action}`, "Completed", documentId);
    await loadDocuments();
  }

  async function downloadDocument(document: DocumentRecord) {
    if (!token) return;
    const response = await fetch(`${apiBase}/api/v1/documents/${document.document_id}/download`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) {
      setStatus("Download failed or this role cannot access the file.");
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

  function toggleRole(role: string) {
    setAllowedRoles((roles) =>
      roles.includes(role) ? roles.filter((item) => item !== role) : [...roles, role]
    );
  }

  return (
    <div className="space-y-5">
      <section className="rounded-md border border-border bg-white p-4">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted">
              <Badge tone="success">ACME Corporation</Badge>
              <Badge tone={token ? "success" : "danger"}>{token ? "Session Active" : "Not Signed In"}</Badge>
              <Badge tone="accent">Tenant Isolated</Badge>
              <Badge tone="accent">RBAC Enforced</Badge>
            </div>
            <h2 className="mt-3 text-xl font-semibold">ACME Enterprise AI Knowledge Workspace</h2>
            <p className="mt-1 max-w-3xl text-sm text-muted">
              Upload governed documents, assign role visibility, ask grounded questions, and inspect exactly why each answer was allowed and generated.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {navigationSections.map((section) => (
              <button
                key={section}
                className={`rounded-md border px-3 py-2 text-sm capitalize ${activeSection === section ? "border-teal-300 bg-teal-50 text-teal-800" : "border-border bg-white"}`}
                onClick={() => setActiveSection(section)}
                type="button"
              >
                {section}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[360px_1fr]">
        <aside className="space-y-4">
          <div className="rounded-md border border-border bg-white p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <UserRound className="h-4 w-4 text-accent" />
              Enterprise Login
            </div>
            <div className="grid gap-2">
              {(["admin", "viewer"] as const).map((kind) => (
                <button
                  key={kind}
                  className="rounded-md border border-border bg-white p-3 text-left text-sm hover:border-teal-300"
                  onClick={() => useDemoUser(kind)}
                  type="button"
                >
                  <div className="font-medium">{demoUsers[kind].label}</div>
                  <div className="text-xs text-muted">{demoUsers[kind].username}</div>
                  <div className="mt-1 text-xs text-teal-700">{demoUsers[kind].scope}</div>
                </button>
              ))}
            </div>
            <form className="mt-3 space-y-2" onSubmit={login}>
              <input
                className="w-full rounded-md border border-border px-3 py-2 text-sm"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Username"
              />
              <div className="flex gap-2">
                <input
                  className="min-w-0 flex-1 rounded-md border border-border px-3 py-2 text-sm"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Password"
                />
                <button className="rounded-md border border-border px-3" type="button" onClick={() => setShowPassword(!showPassword)} title="Toggle password visibility">
                  <Eye className="h-4 w-4" />
                </button>
              </div>
              <div className="text-xs text-muted">Password quality: 8+ characters, mixed case, number, special character.</div>
              <button className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white">
                <LogIn className="h-4 w-4" />
                Sign in with Keycloak
              </button>
            </form>
            {claims ? (
              <div className="mt-3 rounded-md border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
                <div className="font-semibold">Signed in as {claims.subject}</div>
                <div className="mt-1 text-xs">Organization: ACME Corporation</div>
                <div className="text-xs">Tenant: {claims.tenant}</div>
                <div className="text-xs">Roles: {claims.roles.join(", ")}</div>
                <div className="mt-2 text-xs">Access scope: {isAdmin ? "Tenant administration and governed repository management" : "Viewer documents only"}</div>
                <button className="mt-3 rounded-md border border-teal-300 px-3 py-1 text-xs" onClick={logout} type="button">Logout</button>
              </div>
            ) : null}
            <button className="mt-3 inline-flex items-center gap-2 text-xs text-muted" type="button" onClick={() => setShowToken(!showToken)}>
              <KeyRound className="h-3 w-3" />
              {showToken ? "Hide token" : "Show token"}
            </button>
            {showToken ? (
              <textarea className="mt-2 min-h-16 w-full rounded-md border border-border px-3 py-2 text-xs" value={token} onChange={(event) => setToken(event.target.value)} />
            ) : null}
          </div>

          <div className="rounded-md border border-border bg-white p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <ShieldCheck className="h-4 w-4 text-accent" />
              Governance Model
            </div>
            <div className="space-y-2 text-xs text-muted">
              <div>1. Keycloak authenticates users and signs role claims.</div>
              <div>2. Backend resolves tenant and roles from the JWT.</div>
              <div>3. RBAC filters allowed document IDs before retrieval.</div>
              <div>4. Dense search, BM25, RRF, reranking, context, and answer generation only see authorized evidence.</div>
            </div>
          </div>
        </aside>

        <main className="space-y-4">
          {activeSection === "dashboard" ? (
            <Dashboard summary={summary} documents={documents} claims={claims} activity={activity} />
          ) : null}
          {activeSection === "documents" ? (
            <DocumentsSection
              isAdmin={isAdmin}
              token={token}
              documents={filteredDocuments}
              repositorySearch={repositorySearch}
              repositoryFilter={repositoryFilter}
              setRepositorySearch={setRepositorySearch}
              setRepositoryFilter={setRepositoryFilter}
              classification={classification}
              setClassification={setClassification}
              allowedRoles={allowedRoles}
              toggleRole={toggleRole}
              setFile={setFile}
              uploadFile={uploadFile}
              upload={upload}
              documentAction={documentAction}
              downloadDocument={downloadDocument}
              loadDocuments={() => loadDocuments()}
            />
          ) : null}
          {activeSection === "ask" ? (
            <AskSection query={query} setQuery={setQuery} askQuestion={askQuestion} chat={chat} status={status} />
          ) : null}
          {activeSection === "activity" ? (
            <ActivitySection activity={activity} documents={documents} />
          ) : null}
          {activeSection === "evaluation" ? (
            <EvaluationSection askQuestion={askQuestion} />
          ) : null}
          {activeSection === "admin" ? (
            <AdminSection isAdmin={isAdmin} claims={claims} documents={documents} summary={summary} />
          ) : null}
          {status ? <div className="rounded-md border border-border bg-white px-3 py-2 text-sm text-muted">{status}</div> : null}
        </main>
      </section>
    </div>
  );
}

function Dashboard({ summary, documents, claims, activity }: { summary: { totalDocuments: number; indexedChunks: number; restrictedDocuments: number; archivedDocuments: number }; documents: DocumentRecord[]; claims: Claims | null; activity: ActivityEvent[] }) {
  return (
    <section className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={<FileText className="h-4 w-4" />} label="Documents" value={String(summary.totalDocuments)} detail="Visible in current role scope" />
        <MetricCard icon={<Database className="h-4 w-4" />} label="Indexed Chunks" value={String(summary.indexedChunks)} detail="Grounding units available" />
        <MetricCard icon={<LockKeyhole className="h-4 w-4" />} label="Restricted Docs" value={String(summary.restrictedDocuments)} detail="Not visible to viewers" />
        <MetricCard icon={<Archive className="h-4 w-4" />} label="Archived" value={String(summary.archivedDocuments)} detail="Excluded from retrieval" />
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <Panel title="Getting Started Guide">
          <div className="space-y-2 text-sm text-muted">
            <div>1. Sign in to ACME workspace through Keycloak.</div>
            <div>2. Admins upload enterprise documents and assign allowed roles.</div>
            <div>3. Users ask questions; RBAC filters documents before retrieval.</div>
            <div>4. Review citations, grounding quality, and retrieval diagnostics.</div>
          </div>
        </Panel>
        <Panel title="Workspace Context">
          <div className="space-y-2 text-sm">
            <div>Organization: <span className="font-medium">ACME Corporation</span></div>
            <div>Environment: <Badge tone="accent">Local Demo</Badge></div>
            <div>Current User: <span className="font-medium">{claims?.subject ?? "Not signed in"}</span></div>
            <div>Role Scope: <span className="font-medium">{claims?.roles.join(", ") ?? "No active session"}</span></div>
          </div>
        </Panel>
      </div>
      <Panel title="Recent Repository Activity">
        {activity.length ? activity.map((event) => <ActivityRow key={`${event.timestamp}-${event.action}`} event={event} />) : (
          <div className="text-sm text-muted">No activity yet. Sign in, upload a document, or ask a question to populate this timeline.</div>
        )}
      </Panel>
      <Panel title="Recently Indexed Documents">
        <div className="grid gap-2">
          {documents.slice(0, 4).map((document) => <DocumentMini key={document.document_id} document={document} />)}
          {!documents.length ? <div className="text-sm text-muted">No documents uploaded yet.</div> : null}
        </div>
      </Panel>
    </section>
  );
}

function DocumentsSection(props: {
  isAdmin: boolean;
  token: string;
  documents: DocumentRecord[];
  repositorySearch: string;
  repositoryFilter: string;
  setRepositorySearch: (value: string) => void;
  setRepositoryFilter: (value: string) => void;
  classification: string;
  setClassification: (value: string) => void;
  allowedRoles: string[];
  toggleRole: (role: string) => void;
  setFile: (file: File | null) => void;
  uploadFile: (event: FormEvent) => void;
  upload: UploadResult | null;
  documentAction: (documentId: string, action: "archive" | "restore" | "delete" | "permanent") => void;
  downloadDocument: (document: DocumentRecord) => void;
  loadDocuments: () => void;
}) {
  return (
    <section className="space-y-4">
      {props.isAdmin ? (
        <Panel title="Document Upload And Access Control">
          <form className="space-y-4" onSubmit={props.uploadFile}>
            <div>
              <div className="mb-2 text-sm font-medium">Document Access Control</div>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
                {roleOptions.map((role) => (
                  <button key={role} className={`rounded-md border p-3 text-left text-sm ${props.allowedRoles.includes(role) ? "border-teal-300 bg-teal-50" : "border-border bg-white"}`} onClick={() => props.toggleRole(role)} type="button">
                    <div className="font-medium">{role}</div>
                    <div className="text-xs text-muted">Can retrieve if assigned</div>
                  </button>
                ))}
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-[220px_1fr_auto]">
              <select className="rounded-md border border-border px-3 py-2 text-sm" value={props.classification} onChange={(event) => props.setClassification(event.target.value)}>
                {classificationOptions.map((option) => <option key={option}>{option}</option>)}
              </select>
              <input className="rounded-md border border-border px-3 py-2 text-sm" type="file" accept=".txt,.md,.pdf,.docx,text/plain,text/markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={(event) => props.setFile(event.target.files?.[0] ?? null)} />
              <button className="inline-flex items-center justify-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white">
                <UploadCloud className="h-4 w-4" />
                Upload
              </button>
            </div>
            {props.upload ? (
              <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800">
                Indexed {props.upload.title}: {props.upload.chunk_count} chunks, {props.upload.classification}, roles {props.upload.allowed_roles.join(", ")}.
              </div>
            ) : null}
          </form>
        </Panel>
      ) : (
        <Panel title="Repository Access">
          <div className="text-sm text-muted">Viewer role can browse and ask questions against approved documents. Upload and lifecycle controls are hidden because your current role cannot manage the repository.</div>
        </Panel>
      )}

      <Panel title="Documents Repository">
        <div className="mb-3 grid gap-2 md:grid-cols-[1fr_180px_auto]">
          <div className="flex items-center gap-2 rounded-md border border-border px-3">
            <Search className="h-4 w-4 text-muted" />
            <input className="min-w-0 flex-1 py-2 text-sm outline-none" value={props.repositorySearch} onChange={(event) => props.setRepositorySearch(event.target.value)} placeholder="Search filename, uploader, role, classification" />
          </div>
          <select className="rounded-md border border-border px-3 py-2 text-sm" value={props.repositoryFilter} onChange={(event) => props.setRepositoryFilter(event.target.value)}>
            {["All", ...classificationOptions, "Active", "Archived", "Deleted"].map((option) => <option key={option}>{option}</option>)}
          </select>
          <button className="inline-flex items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-sm" onClick={props.loadDocuments} type="button">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="border-b border-border text-xs text-muted">
              <tr>
                <th className="py-2 pr-3">Filename</th>
                <th className="py-2 pr-3">Classification</th>
                <th className="py-2 pr-3">Allowed Roles</th>
                <th className="py-2 pr-3">State</th>
                <th className="py-2 pr-3">Chunks</th>
                <th className="py-2 pr-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {props.documents.map((document) => (
                <tr key={document.document_id} className="border-b border-border align-top">
                  <td className="py-3 pr-3">
                    <div className="font-medium">{document.title}</div>
                    <div className="text-xs text-muted">Uploaded by {document.uploaded_by}</div>
                  </td>
                  <td className="py-3 pr-3"><GovernanceBadge classification={document.classification} /></td>
                  <td className="py-3 pr-3 text-xs">{document.allowed_roles.join(", ")}</td>
                  <td className="py-3 pr-3"><Badge tone={document.state === "Active" ? "success" : "neutral"}>{document.state}</Badge></td>
                  <td className="py-3 pr-3">{document.chunk_count}</td>
                  <td className="py-3 pr-3">
                    <div className="flex flex-wrap gap-2">
                      <button className="inline-flex rounded border border-border p-1" onClick={() => props.downloadDocument(document)} title="Download original file" type="button"><Download className="h-4 w-4" /></button>
                      {props.isAdmin && document.state !== "Archived" ? <button className="rounded border border-border p-1" onClick={() => props.documentAction(document.document_id, "archive")} title="Archive"><Archive className="h-4 w-4" /></button> : null}
                      {props.isAdmin && document.state === "Archived" ? <button className="rounded border border-border p-1" onClick={() => props.documentAction(document.document_id, "restore")} title="Restore"><RotateCcw className="h-4 w-4" /></button> : null}
                      {props.isAdmin ? <button className="rounded border border-red-200 p-1 text-red-700" onClick={() => props.documentAction(document.document_id, "delete")} title="Soft delete"><Trash2 className="h-4 w-4" /></button> : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!props.documents.length ? <div className="p-6 text-center text-sm text-muted">No documents visible in this role scope. Upload a company policy as admin or sign in with a role that has access.</div> : null}
        </div>
      </Panel>
    </section>
  );
}

function AskSection({ query, setQuery, askQuestion, chat, status }: { query: string; setQuery: (value: string) => void; askQuestion: (event?: FormEvent, overrideQuery?: string) => void; chat: ChatResult | null; status: string }) {
  const suggestions = [
    "What are the password requirements?",
    "1. Who gets VPN access? 2. Access reviews are conducted in how many days? 3. What type of Document Classification is this?",
    "Who can approve payroll export?",
    "What question cannot be answered from the uploaded documents?"
  ];
  return (
    <section className="space-y-4">
      <Panel title="Ask Governed Enterprise AI">
        <form className="space-y-3" onSubmit={(event) => askQuestion(event)}>
          <textarea className="min-h-28 w-full rounded-md border border-border px-3 py-2 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} />
          <button className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white">
            <MessageSquareText className="h-4 w-4" />
            Ask with RBAC-safe retrieval
          </button>
        </form>
        <div className="mt-3 flex flex-wrap gap-2">
          {suggestions.map((suggestion) => <button key={suggestion} className="rounded-md border border-border px-3 py-1 text-xs" type="button" onClick={() => askQuestion(undefined, suggestion)}>{suggestion}</button>)}
        </div>
      </Panel>
      {chat ? <AnswerPanel chat={chat} /> : <Panel title="Answer Workspace"><div className="text-sm text-muted">{status || "Ask a question to see grounded answers, citations, retrieval transparency, and hallucination checks."}</div></Panel>}
    </section>
  );
}

function AnswerPanel({ chat }: { chat: ChatResult }) {
  const score = chat.hallucination.score;
  return (
    <section className="space-y-4">
      <Panel title="Grounded Answer">
        <div className="mb-3 flex flex-wrap gap-2">
          <Badge tone={score === 0 ? "success" : score <= 0.35 ? "accent" : "danger"}>Grounding Quality: {trustLabel(score)}</Badge>
          <Badge tone="accent">Citation Validation Enabled</Badge>
          <Badge tone="accent">RBAC Filtered Context</Badge>
        </div>
        <pre className="whitespace-pre-wrap rounded-md border border-teal-200 bg-teal-50 p-3 text-sm text-teal-950">{chat.answer}</pre>
        {chat.hallucination.unsupported_claims.length ? (
          <div className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            Some statements could not be verified: {chat.hallucination.unsupported_claims.join("; ")}
          </div>
        ) : (
          <div className="mt-3 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800">All major claims were supported by retrieved enterprise evidence.</div>
        )}
      </Panel>
      <Panel title="Why This Answer Was Generated">
        <div className="grid gap-3">
          {chat.citations.map((citation) => (
            <div key={citation.citation_id} className="rounded-md border border-border p-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="accent">[{citation.citation_id}]</Badge>
                <span className="font-medium">{citation.source_location?.filename ?? citation.document_id}</span>
                <Badge>{citation.rerank_score > 0 && citation.retrieval_score > 0 ? "Hybrid" : "Retrieved"}</Badge>
                <Badge tone={matchStrength(citation.rerank_score) === "High" ? "success" : "neutral"}>{matchStrength(citation.rerank_score)} match</Badge>
              </div>
              <div className="mt-2 text-xs text-muted">Role Accessibility: allowed by current Keycloak role and document permissions.</div>
              <div className="mt-1 text-xs text-muted">Chunk: {citation.chunk_id}</div>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Advanced Diagnostics">
        <div className="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(chat.retrieval).map(([key, value]) => (
            <div key={key} className="rounded-md border border-border p-2">
              <div className="text-xs text-muted">{key.replaceAll("_", " ")}</div>
              <div className="mt-1 font-semibold">{Array.isArray(value) ? value.length : String(value)}</div>
            </div>
          ))}
        </div>
      </Panel>
    </section>
  );
}

function ActivitySection({ activity, documents }: { activity: ActivityEvent[]; documents: DocumentRecord[] }) {
  return (
    <section className="space-y-4">
      <Panel title="Workspace Activity">
        <div className="space-y-2">
          {activity.length ? activity.map((event) => <ActivityRow key={`${event.timestamp}-${event.action}`} event={event} />) : <div className="text-sm text-muted">No recorded local UI events yet.</div>}
        </div>
      </Panel>
      <Panel title="Audit Visibility Examples">
        <div className="space-y-2 text-sm text-muted">
          <div>Document uploaded → uploader, classification, roles, indexing result.</div>
          <div>Query executed → RBAC was enforced before retrieval.</div>
          <div>Access denied → current role did not match document allowed roles.</div>
          <div>Indexed documents visible in this session: {documents.length}</div>
        </div>
      </Panel>
    </section>
  );
}

function EvaluationSection({ askQuestion }: { askQuestion: (event?: FormEvent, overrideQuery?: string) => void }) {
  const tests = [
    { name: "Security retrieval", query: "Who gets VPN access?", expected: "Remote employees with citation" },
    { name: "RBAC denial", query: "Who can approve payroll export?", expected: "Viewer receives no authorized evidence" },
    { name: "Hallucination prevention", query: "What is ACME's moon base policy?", expected: "Safe insufficient evidence response" },
    { name: "Multi-question", query: "1. Who gets VPN access? 2. What are password requirements? 3. What is the document classification?", expected: "Separate cited answers" }
  ];
  return (
    <Panel title="Evaluation Center">
      <div className="grid gap-3">
        {tests.map((test) => (
          <div key={test.name} className="rounded-md border border-border p-3 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="font-medium">{test.name}</div>
                <div className="text-xs text-muted">Expected: {test.expected}</div>
              </div>
              <button className="rounded-md border border-border px-3 py-1 text-xs" type="button" onClick={() => askQuestion(undefined, test.query)}>Run</button>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function AdminSection({ isAdmin, claims, documents, summary }: { isAdmin: boolean; claims: Claims | null; documents: DocumentRecord[]; summary: { totalDocuments: number; indexedChunks: number; restrictedDocuments: number; archivedDocuments: number } }) {
  return (
    <section className="space-y-4">
      <Panel title="Organization Administration">
        {isAdmin ? (
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-md border border-border p-3 text-sm">
              <div className="font-medium">Organization Users</div>
              <div className="mt-2 text-muted">demo-admin: tenant_admin, manager, employee, viewer</div>
              <div className="text-muted">demo-viewer: viewer</div>
            </div>
            <div className="rounded-md border border-border p-3 text-sm">
              <div className="font-medium">Permission Mapping</div>
              <div className="mt-2 text-muted">Viewer: query approved documents.</div>
              <div className="text-muted">Manager/Employee: upload and query approved documents.</div>
              <div className="text-muted">Tenant Admin: lifecycle, repository, observability.</div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted">Admin governance panels are only rendered for tenant administrators.</div>
        )}
      </Panel>
      <Panel title="Operational Health">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard icon={<Gauge className="h-4 w-4" />} label="Backend" value="Healthy" detail="Ready endpoint online" />
          <MetricCard icon={<Database className="h-4 w-4" />} label="Repository" value={String(summary.totalDocuments)} detail="Documents in role scope" />
          <MetricCard icon={<FileSearch className="h-4 w-4" />} label="Chunks" value={String(summary.indexedChunks)} detail="Indexed evidence" />
          <MetricCard icon={<BarChart3 className="h-4 w-4" />} label="Governance" value="Enabled" detail="Tenant + RBAC + citations" />
        </div>
      </Panel>
      <Panel title="Export And Reporting">
        <pre className="overflow-auto rounded-md border border-border bg-slate-50 p-3 text-xs">{JSON.stringify({ organization: "ACME Corporation", user: claims?.subject, summary, documents: documents.map(({ title, classification, allowed_roles, state }) => ({ title, classification, allowed_roles, state })) }, null, 2)}</pre>
      </Panel>
    </section>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-md border border-border bg-white p-4 shadow-soft">
      <h3 className="mb-3 text-sm font-semibold">{title}</h3>
      {children}
    </section>
  );
}

function MetricCard({ icon, label, value, detail }: { icon: React.ReactNode; label: string; value: string; detail: string }) {
  return (
    <div className="rounded-md border border-border bg-white p-3 shadow-soft">
      <div className="flex items-center gap-2 text-xs text-muted">{icon}{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-muted">{detail}</div>
    </div>
  );
}

function ActivityRow({ event }: { event: ActivityEvent }) {
  return (
    <div className="flex gap-3 rounded-md border border-border p-3 text-sm">
      <Activity className="mt-0.5 h-4 w-4 text-accent" />
      <div>
        <div className="font-medium">{event.action} · {event.result}</div>
        <div className="text-xs text-muted">{event.timestamp} · {event.detail}</div>
      </div>
    </div>
  );
}

function DocumentMini({ document }: { document: DocumentRecord }) {
  return (
    <div className="flex items-center justify-between gap-2 rounded-md border border-border p-2 text-sm">
      <div>
        <div className="font-medium">{document.title}</div>
        <div className="text-xs text-muted">{document.chunk_count} chunks · {document.allowed_roles.join(", ")}</div>
      </div>
      <GovernanceBadge classification={document.classification} />
    </div>
  );
}

function GovernanceBadge({ classification }: { classification: string }) {
  const tone = classification === "Restricted" || classification === "Confidential" ? "danger" : classification === "Internal" ? "accent" : "success";
  return <Badge tone={tone}>{classification}</Badge>;
}
