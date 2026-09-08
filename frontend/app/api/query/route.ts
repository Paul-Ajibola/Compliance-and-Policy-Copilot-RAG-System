import { NextRequest } from "next/server";

/**
 * Proxies POST /api/query to the FastAPI backend's /query endpoint.
 *
 * This is a Next.js Route Handler, not a next.config.ts rewrite —
 * rewrites resolve their destination URL at BUILD time and bake it into
 * the compiled output, which breaks in Docker/Render since env vars
 * aren't injected until the container actually runs. A Route Handler
 * reads process.env fresh on every real request instead.
 */

export async function POST(req: NextRequest) {
  const rawUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
  const backendUrl = rawUrl.startsWith("http") ? rawUrl : `https://${rawUrl}`;
  const body = await req.text();

  const backendRes = await fetch(`${backendUrl}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });

  return new Response(backendRes.body, {
    status: backendRes.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}