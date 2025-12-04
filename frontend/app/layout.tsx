import { Inter } from 'next/font/google';
import Script from 'next/script';
import { Providers } from './providers';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  display: 'swap',
  fallback: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Arial'],
  adjustFontFallback: true,
  preload: true,
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Universal revision detection for cache busting
  const REV =
    process.env.RUNTIME_ENV_REV ||
    process.env.K_REVISION ||
    process.env.VERCEL_GIT_COMMIT_SHA ||
    Date.now().toString();

  return (
    <html lang='en' suppressHydrationWarning className={inter.variable}>
      <head>
        <Script src={`/runtime-env.js?v=${REV}`} strategy='beforeInteractive' />
        <meta name='viewport' content='initial-scale=1, width=device-width' />
        <style>{`
          :root {
            --font-sans: var(--font-inter);
          }
        `}</style>
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
