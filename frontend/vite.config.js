import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth/register':        'http://localhost:8000',
      '/auth/login':           'http://localhost:8000',
      '/auth/me':              'http://localhost:8000',
      '/auth/google':          'http://localhost:8000',
      '/sessions':             'http://localhost:8000',
      '/chat':                 'http://localhost:8000',
      '/orders':               'http://localhost:8000',
      '/health':               'http://localhost:8000',
    }
  }
})