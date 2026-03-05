const API_BASE =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL || '/api')
    : (process.env.BACKEND_URL || 'http://localhost:8000')

function getTgHeaders(): Record<string, string> {
  if (typeof window === 'undefined') return {}
  const tg = (window as any)?.Telegram?.WebApp
  if (!tg?.initData) return {}
  return { 'tg-init-data': tg.initData }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...getTgHeaders(),
      ...(init.headers || {}),
    },
    cache: 'no-store',
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `API error: ${res.status}`)
  }
  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}

// Named endpoint helpers
export const profileApi = {
  getMe: () => api.get('/profiles/me'),
  update: (data: unknown) => api.put('/profiles/me', data),
}
export const gamesApi = {
  list: () => api.get('/games'),
}
export const statsApi = {
  refresh: () => api.post('/account/refresh-stats'),
}
export const accountApi = {
  link: (provider: string, accountRef: string) =>
    api.post(`/account/link/${provider}`, { account_ref: accountRef }),
  list: () => api.get('/account/accounts'),
}
export const matchesApi = {
  getAll: () => api.get('/matches'),
}
export const leaderboardApi = {
  get: (gameId: number, page = 1) =>
    api.get(`/leaderboard/${gameId}?page=${page}`),
}

// Legacy compat — existing code uses backendFetch
export async function backendFetch(path: string, options: RequestInit = {}) {
  return request(path, options)
}
