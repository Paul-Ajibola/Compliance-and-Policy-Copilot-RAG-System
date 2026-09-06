"use client";

import { useState } from "react";

type Props = {
  question: string;
  answer: string;
};

export function FeedbackButtons({ question, answer }: Props) {
  const [rating, setRating] = useState<"up" | "down" | null>(null);
  const [comment, setComment] = useState("");
  const [showComment, setShowComment] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function submit(chosen: "up" | "down", withComment?: string) {
    setRating(chosen);
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, answer, rating: chosen, comment: withComment ?? null }),
      });
    } catch {
      // Feedback is best-effort; a failed submission shouldn't interrupt reading the answer.
    }
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <p className="text-sm" style={{ color: "var(--color-muted)" }}>
        Thanks &mdash; feedback recorded.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-3">
        <span className="text-sm" style={{ color: "var(--color-muted)" }}>
          Was this answer helpful?
        </span>
        <button
          aria-label="Helpful"
          onClick={() => submit("up")}
          className="rounded-sm border px-2 py-1 text-sm"
          style={{ borderColor: "var(--color-rule)" }}
        >
          &#128077;
        </button>
        <button
          aria-label="Not helpful"
          onClick={() => setShowComment(true)}
          className="rounded-sm border px-2 py-1 text-sm"
          style={{ borderColor: "var(--color-rule)" }}
        >
          &#128078;
        </button>
      </div>
      {showComment && (
        <div className="flex flex-col gap-2">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="What was wrong with this answer? (optional)"
            className="w-full rounded-sm border p-2 text-sm"
            style={{ borderColor: "var(--color-rule)", background: "var(--color-paper-raised)" }}
            rows={2}
          />
          <button
            onClick={() => submit("down", comment || undefined)}
            className="self-start rounded-sm border px-3 py-1 text-sm"
            style={{ borderColor: "var(--color-ink)" }}
          >
            Submit feedback
          </button>
        </div>
      )}
    </div>
  );
}
