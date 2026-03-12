/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/e2e/**',
      '**/*.spec.ts',
      '**/LiveLogPanel.test.tsx', // heavy deps; enable when lib/utils etc. exist
    ],
  },
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
        target: 'http://localhost:9000',
        changeOrigin: true,
        secure: false,
        ws: true, // Enable WebSocket proxying for /ws/scan
      },
      '/health': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'http://localhost:9000',
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

