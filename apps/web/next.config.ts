import type { NextConfig } from "next"

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/**",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
