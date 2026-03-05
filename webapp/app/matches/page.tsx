"use client";

import { useEffect, useState } from "react";
import { backendFetch } from "@/lib/api";
import { SkeletonCard } from "@/components/skeleton";

const MOCK_MATCHES = [
    {
        date: '24 февр.',
        summary: { kd: 0.70, dmgPerRound: 123, acs: 183 },
        matches: [
            {
                result: 'loss',
                score: '12:14',
                agent: 'Jett',
                kda: '14/25/13',
                kd: 0.6,
                utilDmg: 11,
                dmgPerRound: 121,
                map: 'Corrode',
                mode: 'Competitive'
            },
            {
                result: 'win',
                score: '13:8',
                agent: 'Omen',
                kda: '16/16/6',
                kd: 1.0,
                utilDmg: 35,
                dmgPerRound: 142,
                map: 'Bind',
                mode: 'Competitive'
            },
        ]
    },
    {
        date: '23 февр.',
        summary: { kd: 1.15, dmgPerRound: 145, acs: 201 },
        matches: [
            {
                result: 'win',
                score: '13:10',
                agent: 'Reyna',
                kda: '22/18/8',
                kd: 1.22,
                utilDmg: 28,
                dmgPerRound: 156,
                map: 'Pearl',
                mode: 'Competitive'
            },
            {
                result: 'win',
                score: '13:5',
                agent: 'Jett',
                kda: '18/12/5',
                kd: 1.5,
                utilDmg: 15,
                dmgPerRound: 167,
                map: 'Abyss',
                mode: 'Competitive'
            },
        ]
    }
];

function getAgentIcon(agent: string): string {
    const icons: Record<string, string> = {
        'Jett': '⚡', 'Omen': '🌀', 'Reyna': '😈', 'Phoenix': '🔥',
        'Sage': '🌿', 'Sova': '🏹', 'Breach': '💥', 'Cypher': '🕵️',
        'Killjoy': '🔧', 'Viper': '🐍', 'Astra': '⭐', 'Kay/O': '🤖',
        'Chamber': '🎩', 'Neon': '⚡', 'Fade': '👻', 'Harbor': '🌊',
        'Deadlock': '🛡️', 'Iso': '⚡'
    };
    return icons[agent] || '🎮';
}

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

    // Use mock data if no real matches
    const displayMatches = matches.length > 0 ? matches : MOCK_MATCHES;

    return (
        <main className="fade-in">
            <div className="hero-banner">
                <div className="hero-logo">ELYX</div>
            </div>

            <div className="section">
                <h2 className="section-title slide-in-left stagger-1">Матчи</h2>

                {displayMatches.length === 0 ? (
                    <div className="card fade-in stagger-2" style={{ textAlign: "center", padding: 24 }}>
                        <div style={{ fontSize: 40, marginBottom: 8 }}>🤝</div>
                        <div style={{ color: "var(--text-muted)", fontSize: 14 }}>
                            Пока нет матчей. Лайкайте профили, чтобы находить тиммейтов!
                        </div>
                    </div>
                ) : (
                    displayMatches.map((group: any, groupIndex: number) => (
                        <div key={group.date} style={{ marginBottom: 20 }}>
                            {/* Date header with summary */}
                            <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center',
                                marginBottom: 8,
                                padding: '0 4px'
                            }}>
                                <div style={{ 
                                    fontSize: 15, 
                                    fontWeight: 600, 
                                    color: 'var(--text-primary)' 
                                }}>
                                    {group.date}
                                </div>
                                <div style={{ 
                                    fontSize: 11, 
                                    color: 'var(--text-secondary)',
                                    display: 'flex',
                                    gap: 12
                                }}>
                                    <span>{group.matches.length} матча</span>
                                    <span>К/Д {group.summary.kd}</span>
                                    <span>У/Р {group.summary.dmgPerRound}</span>
                                    <span>ACS {group.summary.acs}</span>
                                </div>
                            </div>

                            {/* Matches for this date */}
                            {group.matches.map((match: any, i: number) => (
                                <div key={i} className="card fade-in" 
                                    style={{ 
                                        animationDelay: `${0.1 + i * 0.05}s`,
                                        padding: 12,
                                        marginLeft: 4,
                                        borderLeft: `4px solid ${match.result === 'win' ? 'var(--accent-green)' : 'var(--accent-red)'}`
                                    }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                            <div style={{
                                                width: 32, height: 32, borderRadius: '50%',
                                                background: 'var(--bg-card-hover)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontSize: 16
                                            }}>
                                                {getAgentIcon(match.agent)}
                                            </div>
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                    <span style={{ 
                                                        fontSize: 14, 
                                                        fontWeight: 600, 
                                                        color: 'var(--text-primary)' 
                                                    }}>
                                                        {match.score}
                                                    </span>
                                                    <span style={{
                                                        fontSize: 11,
                                                        padding: '2px 6px',
                                                        borderRadius: 4,
                                                        background: match.result === 'win' ? 'var(--accent-green)' : 'var(--accent-red)',
                                                        color: 'white',
                                                        fontWeight: 600
                                                    }}>
                                                        {match.result === 'win' ? 'В' : 'П'}
                                                    </span>
                                                </div>
                                                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                                                    {match.map} • {match.mode}
                                                </div>
                                            </div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                                {match.agent}
                                            </div>
                                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                                                {match.kda}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ 
                                        display: 'flex', 
                                        gap: 16, 
                                        marginTop: 8,
                                        fontSize: 11,
                                        color: 'var(--text-secondary)'
                                    }}>
                                        <span>КД {match.kd}</span>
                                        <span>УПГ% {match.utilDmg}</span>
                                        <span>У/Р {match.dmgPerRound}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))
                )}
            </div>
        </main>
    );
}
