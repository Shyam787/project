import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Enterprise RAG",
  description: "Multi-tenant RAG control surface",
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/enterprise-rag-mark.svg"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
