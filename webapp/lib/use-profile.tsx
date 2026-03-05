"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { backendFetch } from "@/lib/api";

/* ── Types ── */
export interface ProfileData {
    user_id: number;
    tg_id: number;
    username: string;
    nickname: string;
    gender: string;
    age: number | null;
    game_id: number;
    game_name: string;
    bio: string;
    roles: string[];
    tags: string[];
    trust_up: number;
    trust_down: number;
    trust_score: number;
    is_premium: boolean;
    stats: {
        kd: number | null;
        winrate: number | null;
        rank_name: string | null;
        rank_points: number | null;
        unified_score: number;
        source: string;
        source_status: string;
        verified: boolean;
    } | null;
}

export interface GameInfo {
    id: number;
    name: string;
}

export interface LinkedAccount {
    provider: string;
    account_ref: string | null;
    connected: boolean;
}

interface ProfileCtx {
    profile: ProfileData | null;
    games: GameInfo[];
    accounts: LinkedAccount[];
    loading: boolean;
    error: string | null;
    refreshProfile: () => Promise<void>;
    refreshStats: () => Promise<{ ok: boolean; error?: string }>;
    switchGame: (gameId: number) => Promise<void>;
    linkAccount: (provider: string, accountRef: string) => Promise<void>;
}

const ProfileContext = createContext<ProfileCtx | null>(null);

export function useProfile() {
    const ctx = useContext(ProfileContext);
    if (!ctx) throw new Error("useProfile must be used inside ProfileProvider");
    return ctx;
}

/* ── Provider ── */
export function ProfileProvider({ children }: { children: ReactNode }) {
    const [profile, setProfile] = useState<ProfileData | null>(null);
    const [games, setGames] = useState<GameInfo[]>([]);
    const [accounts, setAccounts] = useState<LinkedAccount[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const refreshProfile = useCallback(async () => {
        try {
            setError(null);
            const data = await backendFetch("/profiles/me");
            setProfile(data);
        } catch (e: any) {
            // 404 = no profile yet, not really an error
            if (e?.message?.includes("404")) {
                setProfile(null);
            } else {
                setError("Не удалось загрузить профиль");
            }
        }
    }, []);

    const loadGames = useCallback(async () => {
        try {
            const data = await backendFetch("/games");
            setGames(data);
        } catch { }
    }, []);

    const loadAccounts = useCallback(async () => {
        try {
            const data = await backendFetch("/account/accounts");
            setAccounts(data);
        } catch {
            setAccounts([]);
        }
    }, []);

    const refreshStats = useCallback(async () => {
        try {
            const result = await backendFetch("/account/refresh-stats", { method: "POST" });
            if (result.ok) {
                await refreshProfile();
            }
            return result;
        } catch (e: any) {
            return { ok: false, error: e?.message || "refresh failed" };
        }
    }, [refreshProfile]);

    const switchGame = useCallback(async (gameId: number) => {
        if (!profile) return;
        try {
            setLoading(true);
            await backendFetch("/profiles/me", {
                method: "PUT",
                body: JSON.stringify({
                    nickname: profile.nickname,
                    gender: profile.gender,
                    age: profile.age,
                    game_id: gameId,
                    bio: profile.bio,
                    roles: profile.roles,
                    tags: profile.tags,
                }),
            });
            // Refresh stats for new game
            await backendFetch("/account/refresh-stats", { method: "POST" }).catch(() => { });
            await refreshProfile();
        } catch {
            setError("Не удалось сменить игру");
        } finally {
            setLoading(false);
        }
    }, [profile, refreshProfile]);

    const linkAccount = useCallback(async (provider: string, accountRef: string) => {
        await backendFetch(`/account/link/${provider}`, {
            method: "POST",
            body: JSON.stringify({ account_ref: accountRef }),
        });
        // Refresh stats after linking
        await backendFetch("/account/refresh-stats", { method: "POST" }).catch(() => { });
        await Promise.all([refreshProfile(), loadAccounts()]);
    }, [refreshProfile, loadAccounts]);

    useEffect(() => {
        const init = async () => {
            setLoading(true);
            await Promise.all([refreshProfile(), loadGames(), loadAccounts()]);
            setLoading(false);
        };
        init();
    }, [refreshProfile, loadGames, loadAccounts]);

    return (
        <ProfileContext.Provider value={{
            profile, games, accounts, loading, error,
            refreshProfile, refreshStats, switchGame, linkAccount,
        }}>
            {children}
        </ProfileContext.Provider>
    );
}
