import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "MaterialGPT",
  description: "Scientific RAG para descoberta e comparação de materiais",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
