/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === "production";

const nextConfig = {
  output: "export",
  basePath: isProd ? "/kuuga" : "",
  assetPrefix: isProd ? "/kuuga" : "",
  trailingSlash: true,
};

export default nextConfig;
