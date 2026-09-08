import { NextRequest } from "next/server";

/**
 * Proxies POST /api/feedback to the FastAPI backend's /feedback endpoint.
 *
 * This is a Next.js Route Handler, not a next.config.ts rewrite. That
 * distinction matters: rewrites resolve their destination URL at BUILD
 * time and bake it into the compiled output. In a Docker build, that
 * happens before docker-compose's (or Render's) environment variables
 * are ever injected — so a rewrite would silently fall back to the
 * wrong host and stay wrong until the image is rebuilt. A Route Handler
 * reads process.env fresh on every actual request, which is what we
 * need since BACKEND_INTERNAL_URL is only known at container/service
 * runtime, not at image build time.
 */


export async function POST(req: NextRequest) {
  const rawUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
  const backendUrl = rawUrl.startsWith("http") ? rawUrl : `https://${rawUrl}`;
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

