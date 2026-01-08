import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true, // Enable WebSocket proxying for /ws/scan
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  // Environment variable prefix
  envPrefix: 'VITE_',
})

