import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_PROXY_TARGET ?? 'http://127.0.0.1:8000'
  const devPort = Number(env.VITE_DEV_SERVER_PORT ?? 3000)
  const proxyBasePath = (env.VITE_DEV_API_PREFIX ?? '/api').replace(/\/+$/, '') || '/api'
  const proxyPattern = new RegExp(`^${proxyBasePath.replace(/\//g, '\/')}`)

  return {
    plugins: [react()],
    server: {
      port: devPort,
      proxy: {
        [proxyBasePath]: {
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(proxyPattern, ''),
        },
      },
    },
  }
})
