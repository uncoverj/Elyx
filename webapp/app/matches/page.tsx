"use client";

import { useEffect, useState } from "react";
import { backendFetch } from "@/lib/api";
import { SkeletonCard } from "@/components/skeleton";

export default function HistoryPage() {
    const [matches, setMatches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await backendFetch("/matches");
                setMatches(data || []);
            } catch {
                setMatches([]);
            }
            setLoading(false);
        };
        load();
    }, []);

    if (loading) {
        return (
            <main className="fade-in" style={{ padding: 16 }}>
                {[1, 2, 3, 4].map(i => <div key={i} style={{ marginBottom: 10 }}><SkeletonCard lines={2} /></div>)}
            </main>
        );
    }

    return (
        <main className="fade-in">
            <div className="hero-banner">
                <div className="hero-logo">ELYX</div>
            </div>

            <div className="section">
                <h2 className="section-title slide-in-left stagger-1">Матчи</h2>

                {matches.length === 0 ? (
                    <div className="card fade-in stagger-2" style={{ textAlign: "center", padding: 24 }}>
                        <div style={{ fontSize: 40, marginBottom: 8 }}>🤝</div>
                        <div style={{ color: "var(--text-muted)", fontSize: 14 }}>
                            Пока нет матчей. Лайкайте профили, чтобы находить тиммейтов!
                        </div>
                    </div>
                ) : (
                    matches.map((m: any, i: number) => (
                        <div key={m.match_id} className="match-row fade-in" style={{ animationDelay: `${0.1 + i * 0.05}s` }}>
                            <div className="match-agent-icon" style={{
                                background: "linear-gradient(135deg, rgba(167,139,250,0.2), rgba(167,139,250,0.05))",
                                border: "1px solid rgba(167,139,250,0.3)", fontSize: 13, fontWeight: 700,
                                color: "var(--accent-purple)",
                            }}>
                                {m.nickname?.charAt(0).toUpperCase() || "?"}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: 14 }}>{m.nickname}</div>
                                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                                    @{m.username} • {m.game_name}
                                </div>
                            </div>
                            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                                {m.created_at ? new Date(m.created_at).toLocaleDateString("ru") : ""}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </main>
    );
}
