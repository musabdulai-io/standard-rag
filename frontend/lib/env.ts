import { ENV_SCHEMA, type EnvKey } from './env.schema';

declare global {
  interface Window {
    __ENV?: Record<string, string>;
  }
}

/**
 * Get environment variable value (works server-side and client-side)
 *
 * Server: reads from process.env
 * Client: reads from window.__ENV
 *
 * @param key - Environment variable key from ENV_SCHEMA
 * @returns The environment variable value
 * @throws Error if key not in schema or value is missing
 *
 * @example
 * // In server components
 * const apiUrl = getEnv('NEXT_PUBLIC_API_URL');
 *
 * @example
 * // In client components
 * 'use client';
 * const apiUrl = getEnv('NEXT_PUBLIC_API_URL');
 */
export function getEnv(key: EnvKey): string {
  // Validate key exists in schema
  if (!(key in ENV_SCHEMA)) {
    throw new Error(`Invalid env key: ${key}`);
  }

  const value =
    typeof window === 'undefined'
      ? process.env[key] // Server: read from process.env
      : window.__ENV?.[key]; // Client: read from window.__ENV

  if (!value) {
    throw new Error(`Missing required env var: ${key}`);
  }

  return value;
}
