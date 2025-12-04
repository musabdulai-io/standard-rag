// frontend/lib/session.ts
/**
 * Session management for user isolation.
 * Each browser gets a unique session ID stored in localStorage.
 * This allows users to have private documents without authentication.
 */

const SESSION_KEY = 'standard-rag-session-id';

/**
 * Generate a UUID v4.
 */
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get or create a session ID for the current browser.
 * Generates a unique UUID per browser for user isolation.
 * Sample docs use a fixed ID and are included in searches via backend filter.
 * Returns empty string during SSR.
 */
export function getSessionId(): string {
  if (typeof window === 'undefined') {
    return '';
  }

  let sessionId = localStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }

  return sessionId;
}

/**
 * Clear the session ID (for testing purposes).
 */
export function clearSessionId(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(SESSION_KEY);
  }
}
