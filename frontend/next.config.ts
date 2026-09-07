import type { NextConfig } from "next";

// Proxies /api/query and /api/feedback to the FastAPI backend. This runs
// server-side inside the Next.js container, so the browser only ever
// talks to its own origin — no CORS configuration needed on the backend.
const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/query", destination: `${backendUrl}/query` },
      { source: "/api/feedback", destination: `${backendUrl}/feedback` },
    ];
  },
};

export default nextConfig;