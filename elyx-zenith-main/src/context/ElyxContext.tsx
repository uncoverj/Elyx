import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { backendApi, BackendGame, BackendProfile, initTelegramWebAppTheme, LinkedAccount } from "@/lib/api";

interface ElyxContextValue {
  profile: BackendProfile | null;
  games: BackendGame[];
  accounts: LinkedAccount[];
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
  refreshStats: () => Promise<{ ok: boolean; error?: string }>;
  switchGame: (gameId: number) => Promise<{ ok: boolean; error?: string }>;
  linkAccount: (provider: string, accountRef: string) => Promise<{ ok: boolean; error?: string }>;
}

const ElyxContext = createContext<ElyxContextValue | null>(null);

function buildProfilePayload(profile: BackendProfile, gameId: number) {
  return {
    nickname: profile.nickname,
    gender: profile.gender,
    age: profile.age,
    game_id: gameId,
    bio: profile.bio,
    media_type: profile.media_type,
    media_file_id: profile.media_file_id,
    roles: profile.roles ?? [],
    tags: profile.tags ?? [],
    green_flags: profile.green_flags ?? [],
    dealbreaker: profile.dealbreaker ?? null,
    mood_status: profile.mood_status ?? null,
  };
}

export function ElyxProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<BackendProfile | null>(null);
  const [games, setGames] = useState<BackendGame[]>([]);
  const [accounts, setAccounts] = useState<LinkedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [gamesData, accountsData] = await Promise.all([
        backendApi.getGames(),
        backendApi.getAccounts(),
      ]);
      setGames(gamesData);
      setAccounts(accountsData);

      try {
        const profileData = await backendApi.getProfile();
        setProfile(profileData);
      } catch (profileErr: any) {
        if (String(profileErr?.message || "").includes("Profile not found")) {
          setProfile(null);
        } else {
          throw profileErr;
        }
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshStats = useCallback(async () => {
    try {
      const res = await backendApi.refreshStats();
      if (!res.ok) {
        return { ok: false, error: res.error || res.detail || "Could not refresh stats" };
      }
      const profileData = await backendApi.getProfile();
      setProfile(profileData);
      return { ok: true };
    } catch (err: any) {
      return { ok: false, error: err?.message || "Could not refresh stats" };
    }
  }, []);

  const switchGame = useCallback(
    async (gameId: number) => {
      if (!profile) return { ok: false, error: "Profile not found" };

      try {
        const updated = await backendApi.updateProfile(buildProfilePayload(profile, gameId));
        setProfile(updated);
        return { ok: true };
      } catch (err: any) {
        return { ok: false, error: err?.message || "Could not switch game" };
      }
    },
    [profile]
  );

  const linkAccount = useCallback(async (provider: string, accountRef: string) => {
    try {
      await backendApi.linkAccount(provider, accountRef.trim());
      const [accountsData, profileData] = await Promise.all([
        backendApi.getAccounts(),
        backendApi.getProfile().catch(() => null),
      ]);
      setAccounts(accountsData);
      if (profileData) setProfile(profileData);
      return { ok: true };
    } catch (err: any) {
      return { ok: false, error: err?.message || "Could not connect account" };
    }
  }, []);

  useEffect(() => {
    initTelegramWebAppTheme();
    refreshData();
  }, [refreshData]);

  const value = useMemo<ElyxContextValue>(
    () => ({
      profile,
      games,
      accounts,
      loading,
      error,
      refreshData,
      refreshStats,
      switchGame,
      linkAccount,
    }),
    [profile, games, accounts, loading, error, refreshData, refreshStats, switchGame, linkAccount]
  );

  return <ElyxContext.Provider value={value}>{children}</ElyxContext.Provider>;
}

export function useElyx() {
  const ctx = useContext(ElyxContext);
  if (!ctx) throw new Error("useElyx must be used inside ElyxProvider");
  return ctx;
}
