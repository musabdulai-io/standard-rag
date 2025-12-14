import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Standard RAG',
    short_name: 'RAG',
    description: 'RAG system with document upload and AI-powered Q&A',
    start_url: '/',
    display: 'standalone',
    background_color: '#faf9f7',
    theme_color: '#6366f1',
    icons: [
      { src: '/web-app-manifest-192x192.png', sizes: '192x192', type: 'image/png' },
      { src: '/web-app-manifest-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
