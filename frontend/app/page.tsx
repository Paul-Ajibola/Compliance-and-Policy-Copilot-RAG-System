"use client";

import { useRef, useState } from "react";
import { streamQuery, type Citation } from "@/lib/querySSE";
import { ConfidenceStamp } from "@/components/ConfidenceStamp";
import { CitationDrawer } from "@/components/CitationDrawer";
import { FeedbackButtons } from "@/components/FeedbackButtons";

type Turn = {
  question: string;
  answer: string;
  citations: Citation[];
  status: "streaming" | "verified" | "escalated" | "error";
  errorMessage?: string;
};

export default function Home() {
  const [history, setHistory] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const current = history[history.length - 1];

  async function ask(question: string) {
    if (!question.trim()) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const turn: Turn = { question, answer: "", citations: [], status: "streaming" };
    setHistory((h) => [...h, turn]);
    setInput("");

    const update = (patch: Partial<Turn>) => {
      setHistory((h) => {
        const next = [...h];
        next[next.length - 1] = { ...next[next.length - 1], ...patch };
        return next;
      });
    };

    await streamQuery(
      question,
      {
        onCitations: (citations) => update({ citations }),
        onToken: (text) =>
          setHistory((h) => {
            const next = [...h];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, answer: last.answer + text };
            return next;
          }),
        onRefused: (message) => update({ answer: message, status: "escalated" }),
        onError: (message) => update({ status: "error", errorMessage: message }),
        onDone: () => update({ status: "verified" }),
      },
      controller.signal
    );
  }

  function renderAnswerWithFootnotes(text: string, citations: Citation[]) {
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (!match) return <span key={i}>{part}</span>;
      const marker = Number(match[1]);
      const citation = citations.find((c) => c.marker === marker);
      if (!citation) return <span key={i}>{part}</span>;
      return (
        <button
          key={i}
          onClick={() => setActiveCitation(citation)}
          className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full border text-xs align-super"
          style={{ borderColor: "var(--color-verified)", color: "var(--color-verified)" }}
          aria-label={`View source ${marker}`}
        >
          {marker}
        </button>
      );
    });
  }

  return (
    <div className="flex min-h-screen">
      <aside
        className="hidden w-64 shrink-0 border-r p-6 sm:block"
        style={{ borderColor: "var(--color-rule)" }}
      >
        <h2 className="text-base">Policy Copilot</h2>
        <p className="mt-1 text-xs" style={{ color: "var(--color-muted)" }}>
          Grounded in your company&rsquo;s actual policy documents.
        </p>
        <div className="mt-8 flex flex-col gap-1">
          {history.map((t, i) => (
            <div
              key={i}
              className="truncate rounded-sm px-2 py-1.5 text-sm"
              style={{ color: "var(--color-muted)" }}
              title={t.question}
            >
              {t.question}
            </div>
          ))}
        </div>
      </aside>

      <main className="flex flex-1 flex-col">
        <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-6 py-10">
          {!current && (
            <div className="flex flex-1 flex-col items-center justify-center text-center">
              <h1 className="text-3xl">Ask about company policy</h1>
              <p className="mt-2 max-w-md text-sm" style={{ color: "var(--color-muted)" }}>
                Every answer is grounded in a specific passage from your policy documents, or the
                system tells you plainly when it can&rsquo;t find one.
              </p>
            </div>
          )}

          {current && (
            <article className="flex-1">
              <div className="text-xs uppercase tracking-wide" style={{ color: "var(--color-muted)" }}>
                Question
              </div>
              <h2 className="mt-1 text-xl">{current.question}</h2>

              <div className="mt-6">
                {current.status === "verified" && <ConfidenceStamp state="verified" />}
                {current.status === "escalated" && <ConfidenceStamp state="escalated" />}
              </div>

              <div className="mt-4 text-base leading-relaxed">
                {current.status === "error" ? (
                  <p style={{ color: "var(--color-escalated)" }}>
                    Something went wrong: {current.errorMessage}
                  </p>
                ) : (
                  renderAnswerWithFootnotes(current.answer, current.citations)
                )}
                {current.status === "streaming" && <span className="animate-pulse">&#9646;</span>}
              </div>

              {current.citations.length > 0 && (
                <div className="mt-8 border-t pt-4" style={{ borderColor: "var(--color-rule)" }}>
                  <div className="text-xs uppercase tracking-wide" style={{ color: "var(--color-muted)" }}>
                    Sources
                  </div>
                  <ol className="mt-2 flex flex-col gap-1">
                    {current.citations.map((c) => (
                      <li key={c.marker}>
                        <button
                          onClick={() => setActiveCitation(c)}
                          className="text-left text-sm underline decoration-dotted"
                          style={{ color: "var(--color-muted)" }}
                        >
                          [{c.marker}] {c.heading_path?.join(" \u203a ") ?? "Untitled section"}
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {(current.status === "verified" || current.status === "escalated") && (
                <div className="mt-8">
                  <FeedbackButtons question={current.question} answer={current.answer} />
                </div>
              )}
            </article>
          )}

          <form
            className="mt-8 flex items-center gap-2 border-t pt-6"
            style={{ borderColor: "var(--color-rule)" }}
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about policy&hellip;"
              className="flex-1 rounded-sm border px-3 py-2 text-base"
              style={{ borderColor: "var(--color-rule)", background: "var(--color-paper-raised)" }}
            />
            <button
              type="submit"
              className="rounded-sm px-4 py-2 text-sm font-medium text-white"
              style={{ background: "var(--color-ink)" }}
            >
              Ask
            </button>
          </form>
        </div>
      </main>

      <CitationDrawer citation={activeCitation} onClose={() => setActiveCitation(null)} />
    </div>
  );
}
