type Props = {
  state: "verified" | "escalated";
};

export function ConfidenceStamp({ state }: Props) {
  const isVerified = state === "verified";
  return (
    <div
      className="inline-flex items-center gap-2 rounded-sm border px-3 py-1 text-sm font-medium"
      style={{
        borderColor: isVerified ? "var(--color-verified)" : "var(--color-escalated)",
        color: isVerified ? "var(--color-verified)" : "var(--color-escalated)",
        background: isVerified ? "var(--color-verified-bg)" : "var(--color-escalated-bg)",
      }}
    >
      <span aria-hidden="true">{isVerified ? "\u2713" : "\u25B3"}</span>
      {isVerified ? "Verified Grounded" : "Escalated to Human Expert"}
    </div>
  );
}
