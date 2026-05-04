import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["better-sqlite3"],
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
    ],
    // Trim sizes — we only ever render at a few discrete widths.
    deviceSizes: [320, 480, 640, 800, 1080],
    imageSizes: [22, 44, 80, 120, 160, 220, 300, 600],
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
