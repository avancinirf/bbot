import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuração do Vite com proxy para o backend FastAPI (localhost:8000)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
