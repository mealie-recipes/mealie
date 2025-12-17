import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    // Fallback provided in case the env var is missing during a build check
    const rawUrl = process.env.BACKEND_URL || "http://localhost:9000";
    const backendUrl = rawUrl.replace(/\/$/, "");

    return [
      {
        source: "/api/:path*",
        // Interpolate the URL here
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
