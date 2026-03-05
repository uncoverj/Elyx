"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface MatchEntry {
    id: number;
    result: "win" | "loss";
    score: string;
    kda: string;
    kd: string;
    dmg: string;
    map: string;
    mode: string;
    agent: string;
    agentEmoji: string;
    agentColor: string;
    date: string;
}

// Mock history data — replace with real API call when available
const MOCK_HISTORY: MatchEntry[] = [
    { id: 1, result: "win", score: "13-7", kda: "22/14/5", kd: "1.57", dmg: "147", map: "Ascent", mode: "Competitive", agent: "Jett", agentEmoji: "🗡️", agentColor: "#4A9EFF", date: "Сегодня" },
    { id: 2, result: "loss", score: "9-13", kda: "18/19/4", kd: "0.95", dmg: "128", map: "Haven", mode: "Competitive", agent: "Neon", agentEmoji: "⚡", agentColor: "#3FB950", date: "Сегодня" },
    { id: 3, result: "win", score: "13-5", kda: "25/10/8", kd: "2.50", dmg: "178", map: "Bind", mode: "Competitive", agent: "Jett", agentEmoji: "🗡️", agentColor: "#4A9EFF", date: "Сегодня" },
    { id: 4, result: "loss", score: "11-13", kda: "14/16/6", kd: "0.88", dmg: "112", map: "Fracture", mode: "Competitive", agent: "Brimstone", agentEmoji: "🔥", agentColor: "#E67E22", date: "Вчера" },
    { id: 5, result: "win", score: "13-10", kda: "20/15/7", kd: "1.33", dmg: "143", map: "Pearl", mode: "Spike Rush", agent: "Jett", agentEmoji: "🗡️", agentColor: "#4A9EFF", date: "Вчера" },
    { id: 6, result: "win", score: "13-8", kda: "19/12/3", kd: "1.58", dmg: "158", map: "Lotus", mode: "Competitive", agent: "Neon", agentEmoji: "⚡", agentColor: "#3FB950", date: "Вчера" },
    { id: 7, result: "loss", score: "6-13", kda: "11/17/4", kd: "0.65", dmg: "98", map: "Icebox", mode: "Competitive", agent: "Killjoy", agentEmoji: "🤖", agentColor: "#F0A500", date: "2 дня назад" },
    { id: 8, result: "win", score: "13-11", kda: "22/18/6", kd: "1.22", dmg: "136", map: "Sunset", mode: "Competitive", agent: "Jett", agentEmoji: "🗡️", agentColor: "#4A9EFF", date: "2 дня назад" },
];

function groupByDate(matches: MatchEntry[]) {
    const groups: Record<string, MatchEntry[]> = {};
    for (const m of matches) {
        if (!groups[m.date]) groups[m.date] = [];
        groups[m.date].push(m);
    }
    return groups;
}

export default function MatchesPage() {
    const [matches, setMatches] = useState<MatchEntry[]>(MOCK_HISTORY);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Try to load real matches, fall back to mock silently
        api.get<any[]>("/matches").then(data => {
            if (Array.isArray(data) && data.length > 0) {
                // Transform real data if returned
                setMatches(data as any);
            }
        }).catch(() => { });
    }, []);

    if (loading) {
        return (
            <main>
                <div className="loading-screen">
                    <div className="spinner" />
                </div>
            </main>
        );
    }

    if (!matches.length) {
        return (
            <main className="fade-in">
                <div className="empty-state">
                    <div className="empty-icon-wrap">💞</div>
                    <p className="empty-title">Пока нет матчей</p>
                    <p className="empty-desc">Лайкайте профили в боте, чтобы находить тиммейтов</p>
                    <button className="btn-gradient">Открыть бота</button>
                </div>
            </main>
        );
    }

    const groups = groupByDate(matches);

    return (
        <main className="fade-in">
            {/* Header */}
            <div className="hero-banner" style={{ height: 120, background: "linear-gradient(180deg, rgba(255,70,85,0.12) 0%, transparent 100%)" }}>
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
                <span className="hero-elyx-logo">ELYX</span>
                <div className="hero-content">
                    <h1 style={{ fontSize: 22, fontWeight: 900, color: "var(--text-primary)" }}>🕐 История матчей</h1>
                </div>
            </div>

            {/* Filter pills */}
            <div className="filter-pills" style={{ paddingTop: 8 }}>
                {["Все", "Побед", "Поражений", "Competitive", "Spike Rush"].map((f, i) => (
                    <button key={f} className={`filter-pill${i === 0 ? " active" : ""}`}>{f}</button>
                ))}
            </div>

            {/* Match groups */}
            <div style={{ padding: "0 16px 24px", display: "flex", flexDirection: "column", gap: 16 }}>
                {Object.entries(groups).map(([date, dayMatches]) => (
                    <div key={date}>
                        <p style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.6px" }}>
                            {date}
                        </p>
                        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                            {dayMatches.map(m => (
                                <div key={m.id} className={`match-card ${m.result}`}>
                                    <div className="match-card-stripe" />
                                    <div className="match-card-inner">
                                        {/* Agent */}
                                        <div className="match-agent-wrap">
                                            <div className="match-agent-img" style={{
                                                background: `${m.agentColor}20`,
                                                border: `1px solid ${m.agentColor}40`,
                                                display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20
                                            }}>
                                                {m.agentEmoji}
                                            </div>
                                            <div className={`match-result-badge ${m.result}`}>
                                                {m.result === "win" ? "В" : "П"}
                                            </div>
                                        </div>

                                        {/* Score */}
                                        <div className="match-score">{m.score}</div>

                                        {/* Stats */}
                                        <div className="match-stats">
                                            <p style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                                                KDA <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{m.kda}</span>
                                            </p>
                                            <div className="match-stats-row">
                                                <span className="match-stat-label">КД <span className="match-stat-val">{m.kd}</span></span>
                                                <span className="match-stat-label">У/Р <span className="match-stat-val">{m.dmg}</span></span>
                                            </div>
                                        </div>

                                        {/* Map */}
                                        <div className="match-meta">
                                            <p className="match-map">{m.map}</p>
                                            <p className="match-mode">{m.mode}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
}
