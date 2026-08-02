import type { NextConfig } from "next";

const repo = "/investment-market-dashboard";

const nextConfig: NextConfig = {
  output: "export",
  basePath: repo,
  assetPrefix: repo,
  trailingSlash: true,
};

export default nextConfig;
