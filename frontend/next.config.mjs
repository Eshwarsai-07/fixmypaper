/** @type {import('next').NextConfig} */
const nextConfig = {
  // 100% Serverless - No rewrites needed as we use the App Router API routes directly.
  output: 'standalone',
};

export default nextConfig;
