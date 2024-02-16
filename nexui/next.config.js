/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: "/api/py/:path*",
        destination: process.env.NEXT_PUBLIC_APP_API_ENDPOINT + "/:path*", // Proxy to Backend
      },
    ];
  },
  images: {
    domains: ["utfs.io"],
  },
};

module.exports = nextConfig;
