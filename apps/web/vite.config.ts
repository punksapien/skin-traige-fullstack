import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  base: '/static/',
  build: {
    outDir: 'dist',
  },
  server: {
    port: 3000,
  },
  publicDir: 'public',
});
