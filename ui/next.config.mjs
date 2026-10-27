/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production'

const nextConfig = {
  output: 'export',
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  ...(isProd
    ? {}
    : {
        async rewrites() {
          return [
            {
              source: '/api/:path*',
              destination: process.env.API_URL
                ? `${process.env.API_URL}/api/:path*`
                : 'http://127.0.0.1:8000/api/:path*',
            },
          ]
        },
      }),
}

export default nextConfig
