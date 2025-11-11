import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/health': 'http://localhost:8000',
      '/info': 'http://localhost:8000',
      '/analyze': 'http://localhost:8000',
    }
  },
  preview: {
    port: 3000,
    host: true, // Listen on all addresses
    allowedHosts: [
      'forex-agent-frontend-production.up.railway.app',
      '.railway.app', // Allow all Railway domains
    ]
  }
})
