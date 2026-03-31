/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/api/:path*`,
      },
      {
        source: "/upload",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/upload`,
      },
      {
        source: "/download/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/download/:path*`,
      },
      {
        source: "/results/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/results/:path*`,
      },
    ];
  },
};

export default nextConfig;
