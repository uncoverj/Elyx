"use client";

import { useProfile } from "@/lib/use-profile";
import { SkeletonCard } from "@/components/skeleton";

const MOCK_ROLES = [
    { name: 'Duelist', icon: '⚔️', matches: 58, winRate: 62.1, kd: 0.94, dmg: 147.3, color: '#FF6B35' },
    { name: 'Controller', icon: '🛡️', matches: 41, winRate: 56.1, kd: 0.87, dmg: 127.0, color: '#4A9EFF' },
    { name: 'Initiator', icon: '💥', matches: 4, winRate: 75.0, kd: 1.22, dmg: 137.7, color: '#4CAF50' },
    { name: 'Sentinel', icon: '🔒', matches: 1, winRate: 100.0, kd: 0.94, dmg: 130.5, color: '#FFFFFF' },
];

const MOCK_AGENTS = [
    { name: 'Jett', time: '27ч 54м', winRate: 62.0, kd: 0.94, dmg: 149.4 },
    { name: 'Omen', time: '15ч 11м', winRate: 55.2, kd: 0.96, dmg: 135.0 },
];

const MOCK_MAPS = [
    { name: 'Pearl', record: '15W-4L', winRate: 78.9, kd: 1.01 },
    { name: 'Abyss', record: '10W-3L', winRate: 76.9, kd: 1.11 },
    { name: 'Corrode', record: '8W-4L', winRate: 66.7, kd: 0.85 },
];

export default function RolesPage() {
    const { profile, loading } = useProfile();

    if (loading) {
        return (
            <main className="fade-in" style={{ padding: 16 }}>
                <SkeletonCard lines={3} />
                <div style={{ marginTop: 10 }}><SkeletonCard lines={3} /></div>
                <div style={{ marginTop: 10 }}><SkeletonCard lines={2} /></div>
            </main>
        );
    }

    // Use mock data when no profile
    const displayName = profile?.nickname || "Uncoverj";
    const displayGame = profile?.game_name || "Valorant";

    return (
        <main className="fade-in">
            <div className="hero-banner">
                <div className="hero-logo">{displayGame.substring(0, 4).toUpperCase()}</div>
            </div>

            {/* Mini profile */}
            <div className="profile-header fade-in stagger-1">
                <div className="avatar-ring" style={{ width: 40, height: 40 }}>
                    <div className="avatar-placeholder" style={{ fontSize: 14 }}>{displayName.charAt(0).toUpperCase()}</div>
                </div>
                <div className="profile-info">
                    <div className="profile-name" style={{ fontSize: 16 }}>
                        {displayName} <span className="tag">#{profile?.username || "user"}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {displayGame} • 🎮 {profile?.trust_score?.toFixed(1) || "85.0"}%
                    </div>
                </div>
            </div>

            {/* Roles */}
            <div className="section">
                <h2 className="section-title slide-in-left stagger-2">Роли</h2>
                {MOCK_ROLES.map((role, i) => (
                    <div key={role.name} className="card fade-in" style={{ animationDelay: `${0.1 + i * 0.05}s`, padding: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <div style={{
                                width: 40, height: 40, borderRadius: '50%',
                                background: role.color, display: 'flex',
                                alignItems: 'center', justifyContent: 'center',
                                fontSize: 20
                            }}>
                                {role.icon}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>{role.name}</div>
                                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{role.matches} матчей</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Победы%</div>
                                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{role.winRate}%</div>
                            </div>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>К/Д</div>
                                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{role.kd}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Урон/Раунд</div>
                                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{role.dmg}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Agents */}
            <div className="section">
                <h2 className="section-title slide-in-left stagger-3">Агенты</h2>
                {MOCK_AGENTS.map((agent, i) => (
                    <div key={agent.name} className="card fade-in" style={{ animationDelay: `${0.1 + i * 0.05}s`, padding: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{agent.name}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{agent.time}</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{agent.winRate}%</div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>К/Д {agent.kd}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Maps */}
            <div className="section">
                <h2 className="section-title slide-in-left stagger-4">Карты</h2>
                {MOCK_MAPS.map((map, i) => (
                    <div key={map.name} className="card fade-in" style={{ animationDelay: `${0.1 + i * 0.05}s`, padding: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{map.name}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{map.record}</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{map.winRate}%</div>
                                <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>К/Д {map.kd}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
}
