import type { Citation } from "@/lib/querySSE";

type Props = {
  citation: Citation | null;
  onClose: () => void;
};

export function CitationDrawer({ citation, onClose }: Props) {
  if (!citation) return null;

  const heading = citation.heading_path?.join(" \u203a ") ?? "Untitled section";

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center sm:justify-center"
      style={{ background: "rgba(27,42,51,0.35)" }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Source passage"
    >
      <div
        className="w-full sm:max-w-lg rounded-t-md sm:rounded-md border p-6 shadow-lg"
        style={{ background: "var(--color-paper-raised)", borderColor: "var(--color-rule)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wide" style={{ color: "var(--color-muted)" }}>
              Source [{citation.marker}] &middot; {citation.chunk_type === "table" ? "Table" : "Passage"}
            </div>
            <h3 className="mt-1 text-lg">{heading}</h3>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="shrink-0 text-xl leading-none"
            style={{ color: "var(--color-muted)" }}
          >
            &times;
          </button>
        </div>
        <pre
          className="mt-4 max-h-80 overflow-y-auto whitespace-pre-wrap rounded-sm border p-4 text-sm leading-relaxed"
          style={{
            background: "var(--color-verified-bg)",
            borderColor: "var(--color-rule)",
            fontFamily: "var(--font-body)",
          }}
        >
          {citation.text}
        </pre>
        <p className="mt-3 text-xs" style={{ color: "var(--color-muted)" }}>
          Chunk reference: {citation.chunk_id.slice(0, 8)}&hellip;
        </p>
      </div>
    </div>
  );
}
