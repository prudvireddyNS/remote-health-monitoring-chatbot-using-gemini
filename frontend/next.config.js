/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // Remove appDir since it's no longer needed in newer Next.js versions
  },
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
  },
  images: {
    domains: ['localhost'],
  },
  async redirects() {
    return [];
  },
}

module.exports = nextConfig
