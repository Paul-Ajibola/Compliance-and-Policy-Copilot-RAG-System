import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
  const body = await req.text();

  const backendRes = await fetch(`${backendUrl}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });

  const data = await backendRes.text();
  return new Response(data, {
    status: backendRes.status,
    headers: { "Content-Type": "application/json" },
  });
}