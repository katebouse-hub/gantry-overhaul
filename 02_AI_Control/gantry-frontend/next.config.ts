import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["100.127.48.22"],
  async rewrites() {
    return [
      {
        source: "/api/mastra/:path*",
        destination: "http://localhost:4111/:path*",
      },
    ];
  },
};

export default nextConfig;
