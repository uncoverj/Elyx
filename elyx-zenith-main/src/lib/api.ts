export interface BackendStats {
  kd: number | null;
  winrate: number | null;
  rank_name: string | null;
  rank_points: number | null;
  unified_score: number;
  source: string;
  source_status: string;
  verified: boolean;
}

export interface BackendProfile {
  user_id: number;
  tg_id: number;
  username: string | null;
  nickname: string;
  gender: string;
  age: number;
  game_id: number;
  game_name: string;
  bio: string;
  media_type: string;
  media_file_id: string;
  roles: string[];
  tags: string[];
  green_flags: string[];
  dealbreaker: string | null;
  mood_status: string | null;
  trust_up: number;
  trust_down: number;
  trust_score: number;
  is_premium: boolean;
  stats: BackendStats | null;
}

export interface BackendGame {
  id: number;
  name: string;
}

export interface LinkedAccount {
  provider: string;
  account_ref: string | null;
  connected: boolean;
  verified?: boolean;
}

const DEFAULT_BACKEND_URL = "https://elyx-production.up.railway.app";
const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || DEFAULT_BACKEND_URL).replace(/\/+$/, "");

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};

  const headers: Record<string, string> = {};
  const tgInitData = window.Telegram?.WebApp?.initData;

  if (tgInitData) {
    headers["tg-init-data"] = tgInitData;
    return headers;
  }

  // Fallback for local browser testing without Telegram Mini App.
  const serviceToken = import.meta.env.VITE_SERVICE_TOKEN;
  const telegramId = import.meta.env.VITE_TELEGRAM_ID;
  const telegramUsername = import.meta.env.VITE_TELEGRAM_USERNAME;

  if (serviceToken && telegramId) {
    headers["x-service-token"] = serviceToken;
    headers["x-telegram-id"] = telegramId;
    if (telegramUsername) headers["x-telegram-username"] = telegramUsername;
  }

  return headers;
}

function normalizeErrorBody(payload: unknown): string {
  if (typeof payload === "string") return payload;
  if (payload && typeof payload === "object") {
    const body = payload as Record<string, unknown>;
    if (typeof body.detail === "string") return body.detail;
    if (typeof body.error === "string") return body.error;
  }
  return "Request failed";
}

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...(init.headers || {}),
    },
  });

  const text = await response.text();
  const body = text ? (() => {
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  })() : null;

  if (!response.ok) {
    throw new Error(normalizeErrorBody(body));
  }

  return body as T;
}

export const backendApi = {
  getProfile: () => apiRequest<BackendProfile>("/profiles/me"),
  updateProfile: (payload: Partial<BackendProfile> & { game_id: number }) =>
    apiRequest<BackendProfile>("/profiles/me", { method: "PUT", body: JSON.stringify(payload) }),
  getGames: () => apiRequest<BackendGame[]>("/games"),
  getAccounts: () => apiRequest<LinkedAccount[]>("/account/accounts"),
  linkAccount: (provider: string, accountRef: string) =>
    apiRequest<{ ok: boolean; provider: string; verified: boolean }>(`/account/link/${provider}`, {
      method: "POST",
      body: JSON.stringify({ account_ref: accountRef }),
    }),
  refreshStats: () => apiRequest<{ ok: boolean; error?: string; detail?: string }>("/account/refresh-stats", { method: "POST" }),
};

export function initTelegramWebAppTheme(): void {
  if (typeof window === "undefined") return;
  const app = window.Telegram?.WebApp;
  if (!app) return;

  app.ready();
  app.expand();

  try {
    app.setHeaderColor("#090f2a");
    app.setBackgroundColor("#070c1f");
  } catch {
    // no-op
  }
}
