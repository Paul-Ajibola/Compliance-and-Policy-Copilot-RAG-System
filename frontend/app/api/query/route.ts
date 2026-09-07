import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
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