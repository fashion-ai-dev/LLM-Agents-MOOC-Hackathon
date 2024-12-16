import path from 'node:path';

import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      manifest: {
        name: 'Fashion.ai',
        short_name: 'Fashion.ai',
        description: 'Fashion.ai PWA',
        icons: [
          {
            src: '/fashion-256.png',
            sizes: '256x256',
            type: 'image/png',
          },
          {
            src: '/fashion-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
        start_url: '/',
        display: 'fullscreen',
        background_color: '#ffffff',
        theme_color: '#ffffff',
        orientation: 'portrait',
        scope: '/',
        prefer_related_applications: false,
      },
    }),
  ],
  server: {
    open: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
