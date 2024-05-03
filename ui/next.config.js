/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: "/py/:path*",
        destination: process.env.PYTHON_BACKEND_URL + "/:path*", // Proxy to Backend
      },
    ];
  },
  images: {
    domains: ["utfs.io"],
  },
  distDir: 'dist',
};

module.exports = nextConfig;
