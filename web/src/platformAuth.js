const API_BASE = import.meta.env.VITE_API_BASE
  || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');
const rawFetch = window.fetch.bind(window);
let accessToken = import.meta.env.VITE_PLATFORM_ACCESS_TOKEN || '';

export async function bootstrapPlatformAuth() {
  if (accessToken) return;
  if (!import.meta.env.DEV) {
    throw new Error('VITE_PLATFORM_ACCESS_TOKEN is required for a production dashboard build');
  }
  const response = await rawFetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: 'fusion-dashboard-dev',
      client_secret: 'fusion-dashboard-local-only',
    }),
  });
  if (!response.ok) throw new Error(`Platform authentication failed: HTTP ${response.status}`);
  accessToken = (await response.json()).access_token;
}

export function installAuthenticatedFetch() {
  window.fetch = (input, init = {}) => {
    const headers = new Headers(init.headers || {});
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
    return rawFetch(input, { ...init, headers });
  };
}

export function authenticatedWebSocketUrl(url) {
  if (!accessToken) throw new Error('Platform authentication has not completed');
  const parsed = new URL(url);
  parsed.searchParams.set('access_token', accessToken);
  return parsed.toString();
}
