"use client";

import { useEffect, useState } from "react";
import { useProfile } from "@/lib/use-profile";

const RANK_DISTRIBUTION = [
    { rank: "Iron", pct: 14, h: 14, color: "#6B7280" },
    { rank: "Bronze", pct: 20, h: 20, color: "#A16207" },
    { rank: "Silver", pct: 26, h: 26, color: "#9CA3AF" },
    { rank: "Gold", pct: 18, h: 18, color: "#F0A500" },
    { rank: "Plat", pct: 10, h: 10, color: "#4A9EFF" },
    { rank: "Diamond", pct: 7, h: 7, color: "#818CF8" },
    { rank: "Ascendant", pct: 3, h: 3, color: "#3FB950" },
    { rank: "Immortal", pct: 1.5, h: 2, color: "#EF4444" },
    { rank: "Radiant", pct: 0.5, h: 1, color: "#F9A825" },
];

const MOCK_ROLES = [
    { role: "Duelist", played: 45, pct: 63, wl: "32W 13L", kd: "1.24" },
    { role: "Controller", played: 18, pct: 25, wl: "11W  7L", kd: "1.02" },
    { role: "Sentinel", played: 8, pct: 12, wl: " 4W  4L", kd: "0.91" },
];

const MOCK_AGENTS = [
    { name: "Jett", role: "Duelist", color: "#4A9EFF", games: 28, kd: "1.38" },
    { name: "Neon", role: "Duelist", color: "#3FB950", games: 17, kd: "1.21" },
    { name: "Brimstone", role: "Controller", color: "#E67E22", games: 12, kd: "0.98" },
];

const MOCK_MAPS = [
    { name: "Ascent", wr: 71, games: 14, color: "#4A9EFF" },
    { name: "Haven", wr: 60, games: 10, color: "#3FB950" },
    { name: "Bind", wr: 43, games: 7, color: "#F0A500" },
];

export default function RolesPage() {
    const { profile } = useProfile();
    const [visibleBars, setVisibleBars] = useState(false);
    useEffect(() => { const t = setTimeout(() => setVisibleBars(true), 200); return () => clearTimeout(t); }, []);

    return (
        <main className="fade-in">
            {/* Hero */}
            <div className="hero-banner">
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(255,70,85,0.15) 0%, transparent 60%)" }} />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
                <span className="hero-elyx-logo">ELYX</span>
                <div className="hero-content">
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>
                        {profile?.game_name ?? "Valorant"}
                    </p>
                    <h1 style={{ fontSize: 22, fontWeight: 900, color: "var(--text-primary)" }}>
                        ⚡ Power Stats
                    </h1>
                </div>
            </div>

            {/* Rank Distribution Chart */}
            <div className="section-hd">
                <span className="section-title">Распределение рангов</span>
            </div>
            <div className="rank-chart">
                {RANK_DISTRIBUTION.map(r => (
                    <div key={r.rank} className="rank-chart-bar-wrap">
                        <div
                            className="rank-chart-bar"
                            style={{
                                height: visibleBars ? `${r.h * 4}px` : "2px",
                                background: r.color,
                                opacity: 0.7,
                                transition: `height 0.7s cubic-bezier(0.22,1,0.36,1) ${RANK_DISTRIBUTION.indexOf(r) * 40}ms`
                            }}
                        />
                        <span className="rank-chart-label">{r.rank[0]}</span>
                    </div>
                ))}
            </div>

            {/* Roles Breakdown */}
            <div className="section-hd" style={{ marginTop: 20 }}>
                <span className="section-title">Роли</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10, padding: "0 16px 4px" }}>
                {MOCK_ROLES.map(r => (
                    <div key={r.role} className="card" style={{ padding: "12px 14px" }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                            <div>
                                <p style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>{r.role}</p>
                                <p style={{ fontSize: 11, color: "var(--text-secondary)" }}>{r.played} played · K/D {r.kd}</p>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <p style={{ fontSize: 14, fontWeight: 800, color: "var(--red)" }}>{r.pct}%</p>
                                <p style={{ fontSize: 10, color: "var(--text-secondary)" }}>{r.wl}</p>
                            </div>
                        </div>
                        <div style={{ height: 4, background: "var(--border-default)", borderRadius: 4, overflow: "hidden" }}>
                            <div style={{
                                height: "100%",
                                width: visibleBars ? `${r.pct}%` : "0%",
                                background: "var(--gradient-accent)",
                                transition: "width 0.9s cubic-bezier(0.22,1,0.36,1)",
                                borderRadius: 4
                            }} />
                        </div>
                    </div>
                ))}
            </div>

            {/* Top Agents */}
            <div className="section-hd" style={{ marginTop: 16 }}>
                <span className="section-title">Топ агенты</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "0 16px 4px" }}>
                {MOCK_AGENTS.map((a, i) => (
                    <div key={a.name} className="card" style={{ padding: "12px 14px", display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{
                            width: 40, height: 40, borderRadius: 12, flexShrink: 0,
                            background: `${a.color}20`, border: `1px solid ${a.color}40`,
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: 20
                        }}>
                            {["🗡️", "⚡", "🔥"][i]}
                        </div>
                        <div style={{ flex: 1 }}>
                            <p style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>{a.name}</p>
                            <p style={{ fontSize: 11, color: "var(--text-secondary)" }}>{a.role} · {a.games} games</p>
                        </div>
                        <div style={{ textAlign: "right" }}>
                            <p style={{ fontSize: 15, fontWeight: 800, color: a.color }}>K/D {a.kd}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Best Maps */}
            <div className="section-hd" style={{ marginTop: 16 }}>
                <span className="section-title">Лучшие карты</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, padding: "0 16px 24px" }}>
                {MOCK_MAPS.map(m => (
                    <div key={m.name} className="card" style={{ padding: "12px 14px", display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{
                            width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                            background: `${m.color}20`, border: `1px solid ${m.color}40`,
                            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18
                        }}>🗺️</div>
                        <div style={{ flex: 1 }}>
                            <p style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>{m.name}</p>
                            <p style={{ fontSize: 11, color: "var(--text-secondary)" }}>{m.games} матчей</p>
                        </div>
                        <div>
                            <p style={{ fontSize: 16, fontWeight: 900, color: m.wr >= 55 ? "var(--green)" : m.wr >= 45 ? "var(--gold)" : "var(--red)" }}>
                                {m.wr}%
                            </p>
                            <p style={{ fontSize: 10, color: "var(--text-secondary)", textAlign: "right" }}>WR</p>
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
}
