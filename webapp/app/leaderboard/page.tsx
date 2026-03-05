"use client";

import { useEffect, useState } from "react";
import { useProfile } from "@/lib/use-profile";
import { leaderboardApi } from "@/lib/api";

interface LbEntry {
    rank: number;
    user_id: number;
    nickname: string;
    score: number;
    rank_name: string | null;
    is_premium: boolean;
}

const RANK_DISTRIBUTION = [
    { rank: "Iron", pct: 14, color: "#6B7280" },
    { rank: "Bronze", pct: 20, color: "#A16207" },
    { rank: "Silver", pct: 26, color: "#9CA3AF" },
    { rank: "Gold", pct: 18, color: "#F0A500" },
    { rank: "Plat", pct: 10, color: "#4A9EFF" },
    { rank: "Diamond", pct: 7, color: "#818CF8" },
    { rank: "Ascendant", pct: 3, color: "#3FB950" },
    { rank: "Immortal", pct: 2, color: "#EF4444" },
    { rank: "Radiant", pct: 1, color: "#F9A825" },
];

const MEDALS: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

const TIER_LABELS: Record<number, string> = {
    9: "Radiant", 8: "Immortal", 7: "Ascendant", 6: "Diamond",
    5: "Platinum", 4: "Gold", 3: "Silver", 2: "Bronze", 1: "Iron",
};

const MOCK_ENTRIES: LbEntry[] = [
    { rank: 1, user_id: 101, nickname: "RadiantKing", score: 9800, rank_name: "Radiant", is_premium: true },
    { rank: 2, user_id: 102, nickname: "ImmortalAce", score: 9100, rank_name: "Immortal 3", is_premium: true },
    { rank: 3, user_id: 103, nickname: "TitanSlayer", score: 8750, rank_name: "Immortal 2", is_premium: false },
    { rank: 4, user_id: 104, nickname: "SunshinePro", score: 8200, rank_name: "Ascendant 3", is_premium: false },
    { rank: 5, user_id: 105, nickname: "ValoGhost", score: 7800, rank_name: "Diamond 1", is_premium: true },
    { rank: 6, user_id: 106, nickname: "NeonDragon", score: 7300, rank_name: "Diamond 2", is_premium: false },
    { rank: 7, user_id: 107, nickname: "StealthMode", score: 6900, rank_name: "Platinum 3", is_premium: false },
    { rank: 8, user_id: 108, nickname: "PhoenixRise", score: 6500, rank_name: "Gold 2", is_premium: true },
];

export default function LeaderboardPage() {
    const { profile } = useProfile();
    const [entries, setEntries] = useState<LbEntry[]>(MOCK_ENTRIES);
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        const t = setTimeout(() => setVisible(true), 150);
        if (profile?.game_id) {
            leaderboardApi.get(profile.game_id).then((data: any) => {
                if (Array.isArray(data?.entries) && data.entries.length > 0) {
                    setEntries(data.entries);
                }
            }).catch(() => { });
        }
        return () => clearTimeout(t);
    }, [profile?.game_id]);

    const maxPct = Math.max(...RANK_DISTRIBUTION.map(r => r.pct));

    return (
        <main className="fade-in">
            {/* Hero */}
            <div className="hero-banner" style={{ height: 130, background: "linear-gradient(180deg, rgba(240,165,0,0.15) 0%, transparent 100%)" }}>
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
                <span className="hero-elyx-logo" style={{ background: "linear-gradient(180deg, #F0A500, #FF6B00)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>ELYX</span>
                <div className="hero-content">
                    <h1 style={{ fontSize: 22, fontWeight: 900, color: "var(--text-primary)" }}>🏆 Лидерборд</h1>
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                        {profile?.game_name ?? "Valorant"} · {entries.length} players
                    </p>
                </div>
            </div>

            {/* Rank distribution chart */}
            <div className="section-hd">
                <span className="section-title">Распределение рангов</span>
            </div>
            <div className="rank-chart">
                {RANK_DISTRIBUTION.map((r, i) => (
                    <div key={r.rank} className="rank-chart-bar-wrap">
                        <div
                            className="rank-chart-bar"
                            style={{
                                backgroundColor: r.color,
                                opacity: 0.75,
                                height: visible ? `${(r.pct / maxPct) * 44}px` : "2px",
                                transition: `height 0.7s cubic-bezier(0.22,1,0.36,1) ${i * 40}ms`,
                            }}
                        />
                        <span className="rank-chart-label">{r.rank.slice(0, 2)}</span>
                    </div>
                ))}
            </div>

            {/* Filter pills */}
            <div className="filter-pills" style={{ marginTop: 16 }}>
                {["Все", "Valorant", "CS2", "LoL"].map((f, i) => (
                    <button key={f} className={`filter-pill${i === 0 ? " active" : ""}`}>{f}</button>
                ))}
            </div>

            {/* Leaderboard rows */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "0 16px 24px" }}>
                {entries.map((e) => {
                    const isTop3 = e.rank <= 3;
                    const medal = MEDALS[e.rank];
                    return (
                        <div key={e.user_id} className={`lb-row${isTop3 ? " top3" : ""}`}>
                            {/* Position */}
                            <div className="lb-pos">
                                {medal
                                    ? <span style={{ fontSize: 20 }}>{medal}</span>
                                    : <span className="lb-pos-num">{e.rank}</span>
                                }
                            </div>

                            {/* Avatar placeholder */}
                            <div style={{
                                width: 34, height: 34, borderRadius: "50%", flexShrink: 0,
                                background: isTop3 ? "linear-gradient(135deg, #F0A500, #FF6B00)" : "var(--bg-card-elevated)",
                                border: "1px solid var(--border-default)",
                                display: "flex", alignItems: "center", justifyContent: "center",
                                color: isTop3 ? "#000" : "var(--text-secondary)",
                                fontSize: 14, fontWeight: 800,
                            }}>
                                {e.nickname[0].toUpperCase()}
                            </div>

                            {/* Name */}
                            <div className="lb-name">
                                <p>{e.nickname}{e.is_premium ? " ⭐" : ""}</p>
                                <span>{e.rank_name ?? "Unrated"}</span>
                            </div>

                            {/* Score */}
                            <div className="lb-score">
                                <p className="lb-score-val">{e.score.toLocaleString()}</p>
                                <p className="lb-score-sub">score</p>
                            </div>

                            {/* Tier */}
                            <div className={`lb-tier ${isTop3 ? "top" : "mid"}`}>
                                {isTop3 ? "TOP" : "—"}
                            </div>
                        </div>
                    );
                })}
            </div>
        </main>
    );
}
