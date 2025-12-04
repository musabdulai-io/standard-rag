/**
 * Environment Variable Schema
 *
 * Single source of truth for all production environment variables.
 * All variables use NEXT_PUBLIC_* prefix for universal access.
 *
 * ARCHITECTURE:
 * - Server: Reads from process.env via getEnv()
 * - Client: Reads from window.__ENV via getEnv() (populated by entrypoint.sh)
 *
 * USAGE:
 * import { getEnv } from '@/lib/env';
 * const apiUrl = getEnv('NEXT_PUBLIC_API_URL');
 */

export const ENV_SCHEMA = {
  // API endpoint
  NEXT_PUBLIC_API_URL: {},
} as const;

export type EnvKey = keyof typeof ENV_SCHEMA;
