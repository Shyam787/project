import { ReactNode } from "react";

export function Panel({
  title,
  action,
  children
}: {
  title: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-md border border-border bg-panel p-4 shadow-soft">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

export function Badge({
  tone = "neutral",
  children
}: {
  tone?: "neutral" | "success" | "danger" | "accent";
  children: ReactNode;
}) {
  const tones = {
    neutral: "border-border text-muted",
    success: "border-green-200 bg-green-50 text-green-700",
    danger: "border-red-200 bg-red-50 text-red-700",
    accent: "border-teal-200 bg-teal-50 text-teal-700"
  };
  return (
    <span className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-md border border-border bg-panel p-3 shadow-soft">
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-muted">{detail}</div>
    </div>
  );
}
