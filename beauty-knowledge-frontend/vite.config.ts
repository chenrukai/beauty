import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_DEV_API_TARGET || 'http://127.0.0.1:8080'

  return {
    plugins: [vue()],
    build: {
      chunkSizeWarningLimit: 900,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return undefined
            if (id.includes('element-plus')) return 'vendor-element-plus'
            if (id.includes('echarts')) return 'vendor-echarts'
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) return 'vendor-vue'
            if (id.includes('axios')) return 'vendor-axios'
            return 'vendor-misc'
          }
        }
      }
    },
    server: {
      port: 5173,
      host: true,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true
        }
      }
    }
  }
})
