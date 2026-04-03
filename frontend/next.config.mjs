/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === "production";
const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig = {
  basePath: isProd ? "/kuuga" : "",
  assetPrefix: isProd ? "/kuuga" : "",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
