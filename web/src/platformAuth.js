const API_BASE = import.meta.env.VITE_API_BASE
  || (import.meta.env.DEV ? 'http://localhost:8001' : '');
const rawFetch = window.fetch.bind(window);
let accessToken = window.__FUSION_CONFIG__?.accessToken || '';
let expiresAt = 0;
let refreshPromise = null;

function tokenExpiry(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    return Number(payload.exp || 0);
  } catch {
    return 0;
  }
}

function validateRuntimeConfig() {
  if (!API_BASE) throw new Error('VITE_API_BASE is required for production');
  if (!import.meta.env.DEV && !API_BASE.startsWith('https://')) {
    throw new Error('Production dashboard API must use HTTPS');
  }
}

export async function bootstrapPlatformAuth(force = false) {
  validateRuntimeConfig();
  const now = Math.floor(Date.now() / 1000);
  expiresAt = expiresAt || tokenExpiry(accessToken);
  if (!force && accessToken && expiresAt > now + 30) return;
  if (!import.meta.env.DEV) {
    throw new Error('A current runtime access token is required in window.__FUSION_CONFIG__');
  }
  if (!refreshPromise) {
    refreshPromise = rawFetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: 'fusion-dashboard-dev',
        client_secret: 'fusion-dashboard-local-only',
      }),
    }).then(async (response) => {
      if (!response.ok) throw new Error(`Platform authentication failed: HTTP ${response.status}`);
      const body = await response.json();
      accessToken = body.access_token;
      expiresAt = body.expires_at;
    }).finally(() => {
      refreshPromise = null;
    });
  }
  await refreshPromise;
}

export function installAuthenticatedFetch() {
  window.fetch = async (input, init = {}) => {
    await bootstrapPlatformAuth();
    const headers = new Headers(init.headers || {});
    headers.set('Authorization', `Bearer ${accessToken}`);
    let response = await rawFetch(input, { ...init, headers });
    if (response.status === 401 && import.meta.env.DEV) {
      await bootstrapPlatformAuth(true);
      headers.set('Authorization', `Bearer ${accessToken}`);
      response = await rawFetch(input, { ...init, headers });
    }
    return response;
  };
}

export function authenticatedWebSocketUrl(url) {
  validateRuntimeConfig();
  if (!accessToken || tokenExpiry(accessToken) <= Math.floor(Date.now() / 1000)) {
    throw new Error('Platform authentication has expired');
  }
  const parsed = new URL(url);
  if (!import.meta.env.DEV && parsed.protocol !== 'wss:') {
    throw new Error('Production dashboard WebSocket must use WSS');
  }
  parsed.searchParams.set('access_token', accessToken);
  return parsed.toString();
}

export { API_BASE };
