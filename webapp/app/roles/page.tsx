"use client";

import { useProfile } from "@/lib/use-profile";
import { SkeletonCard } from "@/components/skeleton";

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

    if (!profile) {
        return (
            <main className="fade-in">
                <div className="loading-screen">
                    <div className="loading-logo">ELYX</div>
                    <p style={{ color: "var(--text-muted)", fontSize: 14, textAlign: "center", padding: "0 32px" }}>
                        Профиль не найден. Зарегистрируйся через бота.
                    </p>
                </div>
            </main>
        );
    }

    const s = profile.stats;

    return (
        <main className="fade-in">
            <div className="hero-banner">
                <div className="hero-logo">{profile.game_name?.substring(0, 4).toUpperCase() || "ELYX"}</div>
            </div>

            {/* Mini profile */}
            <div className="profile-header fade-in stagger-1">
                <div className="avatar-ring" style={{ width: 40, height: 40 }}>
                    <div className="avatar-placeholder" style={{ fontSize: 14 }}>{profile.nickname?.charAt(0).toUpperCase()}</div>
                </div>
                <div className="profile-info">
                    <div className="profile-name" style={{ fontSize: 16 }}>
                        {profile.nickname} <span className="tag">#{profile.username}</span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {profile.game_name} • 🎮 {profile.trust_score?.toFixed(1)}%
                    </div>
                </div>
            </div>

            {/* Roles */}
            <div className="section">
                <h2 className="section-title slide-in-left stagger-2">Роли</h2>
                {profile.roles && profile.roles.length > 0 ? (
                    profile.roles.map((role, i) => (
                        <div key={role} className="role-card fade-in" style={{ animationDelay: `${0.1 + i * 0.07}s` }}>
                            <div className="role-icon" style={{ animation: "floatY 3s ease-in-out infinite", animationDelay: `${i * 0.3}s` }}>
                                {role.toLowerCase().includes("duelist") ? "⚔️" :
                                    role.toLowerCase().includes("controller") ? "🌀" :
                                        role.toLowerCase().includes("initiator") ? "🔍" :
                                            role.toLowerCase().includes("sentinel") ? "🛡️" :
                                                role.toLowerCase().includes("carry") ? "⚔️" :
                                                    role.toLowerCase().includes("support") ? "💚" :
                                                        role.toLowerCase().includes("mid") ? "🎯" : "🎮"}
                            </div>
                            <div className="role-info">
                                <div className="role-name">{role}</div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="card fade-in stagger-3" style={{ textAlign: "center", padding: 20 }}>
                        <div style={{ fontSize: 28, marginBottom: 6 }}>🎭</div>
                        <div style={{ color: "var(--text-muted)", fontSize: 13 }}>Роли не указаны. Обнови профиль через бота.</div>
                    </div>
                )}
            </div>

            {/* Stats Summary */}
            <div className="section">
                <h2 className="section-title slide-in-left stagger-4">Сводка</h2>
                {s && (s.kd != null || s.winrate != null || s.rank_name) ? (
                    <div className="stats-grid">
                        {s.rank_name && (
                            <div className="stat-card fade-in stagger-5">
                                <div className="stat-label">Ранг</div>
                                <div className="stat-value">{s.rank_name}</div>
                                {s.rank_points != null && <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{s.rank_points} pts</div>}
                            </div>
                        )}
                        {s.kd != null && (
                            <div className="stat-card fade-in stagger-6">
                                <div className="stat-label">K/D</div>
                                <div className="stat-value">{s.kd.toFixed(2)}</div>
                            </div>
                        )}
                        {s.winrate != null && (
                            <div className="stat-card fade-in stagger-7">
                                <div className="stat-label">Win %</div>
                                <div className="stat-value">{s.winrate.toFixed(1)}%</div>
                            </div>
                        )}
                        {s.unified_score > 0 && (
                            <div className="stat-card fade-in stagger-8">
                                <div className="stat-label">Score</div>
                                <div className="stat-value">{s.unified_score}</div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="card fade-in stagger-5" style={{ textAlign: "center", padding: 20 }}>
                        <div style={{ fontSize: 28, marginBottom: 6 }}>📊</div>
                        <div style={{ color: "var(--text-muted)", fontSize: 13 }}>Нет данных. Привяжи аккаунт в настройках.</div>
                    </div>
                )}
            </div>

            {/* Tags */}
            {profile.tags && profile.tags.length > 0 && (
                <div className="section fade-in stagger-8">
                    <h2 className="section-title">Теги</h2>
                    <div className="badge-row">
                        {profile.tags.map((tag, i) => <span key={i} className="badge-pill">{tag}</span>)}
                    </div>
                </div>
            )}
        </main>
    );
}
