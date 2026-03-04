"use client";

import { useEffect, useState } from "react";
import { useProfile } from "@/lib/use-profile";
import { backendFetch } from "@/lib/api";
import { SkeletonCard } from "@/components/skeleton";

export default function LeaderboardPage() {
    const { profile, games } = useProfile();
    const [entries, setEntries] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [selectedGame, setSelectedGame] = useState<number | null>(null);

    const activeGameId = selectedGame ?? profile?.game_id ?? 1;

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const data = await backendFetch(`/leaderboard/${activeGameId}?limit=50`);
                setEntries(data.entries || []);
                setTotal(data.total || 0);
            } catch {
                setEntries([]);
                setTotal(0);
            }
            setLoading(false);
        };
        load();
    }, [activeGameId]);

    const gameName = games.find(g => g.id === activeGameId)?.name || "Game";

    return (
        <main className="fade-in">
            <div className="hero-banner">
                <div className="hero-logo">{gameName.substring(0, 4).toUpperCase()}</div>
            </div>

            <div className="leaderboard-header fade-in stagger-1">
                <div className="lb-title-row">
                    <div className="lb-icon" style={{ animation: "floatY 2.5s ease-in-out infinite" }}>📊</div>
                    <h2>Лидеры</h2>
                </div>
                <div className="player-count">{total.toLocaleString()} игроков</div>
            </div>

            {/* Game filter tabs */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", padding: "0 16px", marginBottom: 12 }}>
                {games.filter(g => g.name !== "Other").map((g, i) => (
                    <button
                        key={g.id}
                        className={`badge-pill fade-in ${activeGameId === g.id ? "active" : ""}`}
                        style={{ animationDelay: `${0.1 + i * 0.04}s`, cursor: "pointer", fontSize: 11 }}
                        onClick={() => setSelectedGame(g.id)}
                    >
                        {g.name}
                    </button>
                ))}
            </div>

            {loading ? (
                <div style={{ padding: 16 }}>
                    {[1, 2, 3, 4, 5].map(i => <div key={i} style={{ marginBottom: 8 }}><SkeletonCard lines={1} /></div>)}
                </div>
            ) : entries.length === 0 ? (
                <div className="section fade-in" style={{ textAlign: "center", padding: 32 }}>
                    <div style={{ fontSize: 40, marginBottom: 8 }}>🏆</div>
                    <div style={{ color: "var(--text-muted)", fontSize: 14 }}>
                        Лидерборд пуст. Привяжите аккаунты и обновите статистику!
                    </div>
                </div>
            ) : (
                <div>
                    <div className="lb-table-header fade-in stagger-3">
                        <span>#</span><span>Игрок</span><span>Trust</span><span>Score</span><span style={{ textAlign: "right" }}>Ранг</span>
                    </div>
                    {entries.map((e: any, i: number) => (
                        <div key={i} className={`lb-row${e.position <= 3 ? ` lb-row-${["", "gold", "silver", "bronze"][e.position]}` : ""} fade-in`}
                            style={{ animationDelay: `${0.15 + i * 0.03}s` }}>
                            <span className={`lb-rank${e.position <= 3 ? " gold" : ""}`}>
                                {e.position <= 3 ? ["", "🥇", "🥈", "🥉"][e.position] : e.position}
                            </span>
                            <span className="lb-name">{e.nickname}</span>
                            <span className="lb-trust">{(e.trust_score || 0).toFixed(1)}%</span>
                            <span className="lb-rating">{(e.unified_score || e.rank_points || 0).toLocaleString()}</span>
                            <span className="lb-tier">{e.rank_name || "—"}</span>
                        </div>
                    ))}
                </div>
            )}
        </main>
    );
}
