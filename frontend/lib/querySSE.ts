export type Citation = {
  marker: number;
  chunk_id: string;
  chunk_index: number;
  heading_path: string[] | null;
  chunk_type: string;
  text: string;
};

export type QueryEvents = {
  onCitations?: (citations: Citation[]) => void;
  onToken?: (text: string) => void;
  onRefused?: (message: string, topScore: number | null) => void;
  onError?: (message: string) => void;
  onDone?: () => void;
};

/**
 * The backend's /query endpoint streams Server-Sent Events over a POST
 * request. The browser's built-in EventSource API only supports GET, so
 * we read the response body as a raw stream and parse the "event: ...\n
 * data: ...\n\n" frames ourselves.
 */
export async function streamQuery(question: string, handlers: QueryEvents, signal?: AbortSignal) {
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal,
  });

  if (!res.ok || !res.body) {
    handlers.onError?.(`Request failed (${res.status})`);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const eventMatch = frame.match(/^event: (.+)$/m);
      const dataMatch = frame.match(/^data: (.+)$/m);
      if (!eventMatch || !dataMatch) continue;

      const eventName = eventMatch[1].trim();
      let payload: any = {};
      try {
        payload = JSON.parse(dataMatch[1]);
      } catch {
        continue;
      }

      switch (eventName) {
        case "citations":
          handlers.onCitations?.(payload.citations ?? []);
          break;
        case "token":
          handlers.onToken?.(payload.text ?? "");
          break;
        case "refused":
          handlers.onRefused?.(payload.message ?? "", payload.top_score ?? null);
          break;
        case "error":
          handlers.onError?.(payload.message ?? "Unknown error");
          break;
        case "done":
          handlers.onDone?.();
          break;
      }
    }
  }
}
