"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import CrystalViewer from "./components/CrystalViewer";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const STORAGE_KEY = "materialgpt:chat";

type Message = {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  cif?: string;
};

type ProgressStep = {
  node: string;
  label: string;
  iteration: number | null;
};

async function extractErrorMessage(response: Response): Promise<string> {
  const text = await response.text();
  try {
    const data = JSON.parse(text);
    return data.detail ?? text;
  } catch {
    return text || `Erro ${response.status}`;
  }
}

function loadStoredChat(): { messages: Message[]; sessionId: string | null } {
  if (typeof window === "undefined") return { messages: [], sessionId: null };
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { messages: [], sessionId: null };
    const parsed = JSON.parse(raw);
    return { messages: parsed.messages ?? [], sessionId: parsed.sessionId ?? null };
  } catch {
    return { messages: [], sessionId: null };
  }
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const hydrated = useRef(false);

  // Carrega a conversa salva no navegador (sobrevive a reload de página).
  useEffect(() => {
    const stored = loadStoredChat();
    setMessages(stored.messages);
    setSessionId(stored.sessionId);
    hydrated.current = true;
  }, []);

  useEffect(() => {
    if (!hydrated.current) return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ messages, sessionId }));
  }, [messages, sessionId]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || loading) return;

    const currentQuestion = question.trim();
    setMessages((prev) => [...prev, { role: "user", content: currentQuestion }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    setSteps([]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuestion, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(await extractErrorMessage(response));
      }
      if (!response.body) {
        throw new Error("Resposta sem corpo de streaming");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const rawEvent of events) {
          const line = rawEvent.trim();
          if (!line.startsWith("data:")) continue;
          const payload = JSON.parse(line.slice(5).trim());

          if (payload.type === "progress") {
            setSteps((prev) => [
              ...prev,
              { node: payload.node, label: payload.label, iteration: payload.iteration },
            ]);
          } else if (payload.type === "error") {
            throw new Error(payload.detail);
          } else if (payload.type === "done") {
            setSessionId(payload.session_id);
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: payload.report,
                intent: payload.intent,
                cif: payload.structure_cif ?? undefined,
              },
            ]);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
      setSteps([]);
    }
  }

  function handleClear() {
    setMessages([]);
    setSessionId(null);
    window.localStorage.removeItem(STORAGE_KEY);
  }

  return (
    <main className="container">
      <header className="header-row">
        <div>
          <h1>MaterialGPT</h1>
          <p>Scientific RAG para descoberta, comparação e explicação de materiais.</p>
        </div>
        {messages.length > 0 && (
          <button type="button" className="clear-button" onClick={handleClear}>
            Limpar conversa
          </button>
        )}
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <p className="hint">
            Experimente: &quot;Quero um material leve e resistente a 1200°C&quot;,
            &quot;Titânio vs Inconel para alta temperatura&quot; ou &quot;Proponha um substituto
            mais barato para o ouro&quot;.
          </p>
        )}
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.intent && <span className="intent">{message.intent}</span>}
            {message.role === "assistant" ? (
              <>
                {message.cif && <CrystalViewer cif={message.cif} />}
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </>
            ) : (
              <p>{message.content}</p>
            )}
          </div>
        ))}

        {loading && (
          <div className="progress">
            {steps.length === 0 && <p className="hint">Conectando…</p>}
            {steps.map((step, index) => {
              const isCurrent = index === steps.length - 1;
              return (
                <div key={index} className={`progress-step ${isCurrent ? "current" : "done"}`}>
                  <span className="progress-icon">{isCurrent ? "" : "✓"}</span>
                  <span>
                    {step.label}
                    {step.iteration ? ` (tentativa ${step.iteration})` : ""}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {error && <p className="error">{error}</p>}
      </div>

      <form onSubmit={handleSubmit} className="composer">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Pergunte sobre um material, comparação ou propriedade…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          Enviar
        </button>
      </form>
    </main>
  );
}
