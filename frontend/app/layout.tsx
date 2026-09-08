import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

/**
 * next/font/google downloads and self-hosts these fonts at build time
 * (not a runtime request to Google's CDN — better privacy and
 * performance than a plain <link> tag). Each call generates a CSS
 * custom property matching the `variable` name given below.
 */

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600"],
});

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Compliance & Policy Copilot",
  description: "Ask questions about company policy, grounded in your actual documents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${plexSans.variable}`}>{children}</body>
    </html>
  );
}
