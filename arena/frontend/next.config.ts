import type { NextConfig } from "next";

// NOTE: with output:"standalone", next.config rewrites are serialized at BUILD time,
// so API_ORIGIN is baked into the image when it's built (see the frontend Dockerfile's
// ARG) and is NOT overridable at `docker run -e API_ORIGIN=...`. The compose build passes
// it as a build-arg; the in-network origin (http://api:8000) is fixed, so this is intended.
const API_ORIGIN = process.env.API_ORIGIN ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }];
  },
};

export default nextConfig;
