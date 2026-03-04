"use client";

import { useEffect, useState } from "react";
import WebAppInit from "@/components/webapp-init";
import { useProfile } from "@/lib/use-profile";
import { SkeletonProfile } from "@/components/skeleton";

/* ── Game-specific theming ── */
const GAME_THEMES: Record<string, { gradient: string; accent: string; glow: string; icon: string }> = {
  "Valorant": { gradient: "linear-gradient(135deg, #fd4556 0%, #1f1225 100%)", accent: "#fd4556", glow: "rgba(253,69,86,0.3)", icon: "🎯" },
  "CS2": { gradient: "linear-gradient(135deg, #de9b35 0%, #1a1a2e 100%)", accent: "#de9b35", glow: "rgba(222,155,53,0.3)", icon: "🔫" },
  "League of Legends": { gradient: "linear-gradient(135deg, #c89b3c 0%, #091428 100%)", accent: "#c89b3c", glow: "rgba(200,155,60,0.3)", icon: "⚔️" },
  "Dota 2": { gradient: "linear-gradient(135deg, #e44d2e 0%, #1a1a2e 100%)", accent: "#e44d2e", glow: "rgba(228,77,46,0.3)", icon: "🛡️" },
  "Apex Legends": { gradient: "linear-gradient(135deg, #cd3333 0%, #1a1a2e 100%)", accent: "#cd3333", glow: "rgba(205,51,51,0.3)", icon: "🏹" },
  "Overwatch 2": { gradient: "linear-gradient(135deg, #fa9c1e 0%, #1a1a2e 100%)", accent: "#fa9c1e", glow: "rgba(250,156,30,0.3)", icon: "🌟" },
  "Fortnite": { gradient: "linear-gradient(135deg, #9d4dbb 0%, #1a1a2e 100%)", accent: "#9d4dbb", glow: "rgba(157,77,187,0.3)", icon: "🏗️" },
};
const DEFAULT_THEME = { gradient: "linear-gradient(135deg, #a78bfa 0%, #1a0a2e 100%)", accent: "#a78bfa", glow: "rgba(167,139,250,0.3)", icon: "🎮" };

function ProgressBar({ percent, color = "red" }: { percent: number; color?: string }) {
  const [width, setWidth] = useState(0);
  useEffect(() => { const t = setTimeout(() => setWidth(Math.min(100, Math.max(0, percent))), 100); return () => clearTimeout(t); }, [percent]);
  return (
    <div className="progress-bar shimmer-overlay">
      <div className={`progress-fill ${color}`} style={{ width: `${width}%`, transition: "width 0.8s cubic-bezier(0.22,1,0.36,1)" }} />
    </div>
  );
}

function getRankEmoji(rank: string | null): string {
  if (!rank) return "🎮";
  const l = rank.toLowerCase();
  if (l.includes("iron") || l.includes("silver") || l.includes("level 1") || l.includes("level 2")) return "⚪";
  if (l.includes("bronze") || l.includes("gold nova") || l.includes("level 3") || l.includes("level 4")) return "🟤";
  if (l.includes("gold") || l.includes("level 5") || l.includes("level 6")) return "🟡";
  if (l.includes("platinum") || l.includes("master guardian") || l.includes("level 7")) return "🔵";
  if (l.includes("diamond") || l.includes("legendary") || l.includes("level 8") || l.includes("level 9")) return "💎";
  if (l.includes("ascendant") || l.includes("supreme") || l.includes("level 10")) return "💚";
  if (l.includes("immortal") || l.includes("global")) return "🔴";
  if (l.includes("radiant")) return "🌟";
  return "🎮";
}

function getSourceLabel(source: string | null | undefined, gameName: string | undefined): string {
  if (!source) return "";
  if (source === "faceit") return "FACEIT";
  if (source === "riot") return gameName === "Valorant" ? "HENRIK" : "RIOT";
  return source.toUpperCase();
}

function getPointsLabel(source: string | null | undefined): string {
  if (source === "faceit") return "ELO";
  if (source === "riot") return "LP";
  return "RR";
}

export default function ProfilePage() {
  const { profile, loading, error, refreshStats, games, switchGame } = useProfile();
  const [refreshing, setRefreshing] = useState(false);
  const [switching, setSwitching] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshStats();
    setRefreshing(false);
  };

  const handleSwitchGame = async (gameId: number) => {
    if (profile?.game_id === gameId || switching) return;
    setSwitching(true);
    await switchGame(gameId);
    setSwitching(false);
  };

  const theme = GAME_THEMES[profile?.game_name || ""] || DEFAULT_THEME;

  if (loading) {
    return (
      <main>
        <WebAppInit />
        <SkeletonProfile />
      </main>
    );
  }

  if (!profile) {
    return (
      <main>
        <WebAppInit />
        <div className="loading-screen">
          <div className="loading-logo">ELYX</div>
          <p style={{ color: "var(--text-muted)", fontSize: 14, textAlign: "center", padding: "0 32px" }}>
            {error || "Профиль не найден. Зарегистрируйся через бота в Telegram."}
          </p>
        </div>
      </main>
    );
  }

  const s = profile.stats;
  const trustPct = profile.trust_score || 0;

  return (
    <main className="fade-in">
      <WebAppInit />

      {/* Hero Banner — game-themed */}
      <div className="hero-banner" style={{ background: theme.gradient, backgroundSize: "200% 200%", animation: "gradientShift 8s ease infinite" }}>
        <div className="hero-logo">{profile.game_name?.substring(0, 4).toUpperCase() || "ELYX"}</div>
      </div>

      {/* Profile Header */}
      <div className="profile-header fade-in stagger-1">
        <div className="avatar-ring" style={{ background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}88)` }}>
          <div className="avatar-placeholder">{profile.nickname?.charAt(0).toUpperCase() || "?"}</div>
        </div>
        <div className="profile-info">
          <div className="profile-name">
            {profile.is_premium && <span style={{ animation: "floatY 2s ease-in-out infinite" }}>👑</span>}
            {profile.nickname}
            <span className="tag">#{profile.username || "user"}</span>
          </div>
          <div className="trust-row">
            <span>{theme.icon} <span className="trust-pct">{trustPct.toFixed(1)}%</span></span>
            <span className="trust-item">👍 {profile.trust_up}</span>
            <span className="trust-item">👎 {profile.trust_down}</span>
          </div>
        </div>
      </div>

      {/* ── Game Category Tabs ── */}
      <div className="section fade-in stagger-2" style={{ paddingBottom: 4 }}>
        <div className="game-tab-bar">
          {games.filter(g => g.name !== "Other").map((g, i) => {
            const isActive = profile.game_id === g.id;
            const gTheme = GAME_THEMES[g.name] || DEFAULT_THEME;
            return (
              <button
                key={g.id}
                className={`game-tab-btn${isActive ? " active" : ""}`}
                style={{
                  animationDelay: `${0.05 + i * 0.03}s`,
                  "--tab-accent": gTheme.accent,
                  "--tab-glow": gTheme.glow,
                  opacity: switching ? 0.5 : 1,
                } as React.CSSProperties}
                onClick={() => handleSwitchGame(g.id)}
                disabled={switching}
              >
                <span className="game-tab-icon">{(GAME_THEMES[g.name] || DEFAULT_THEME).icon}</span>
                <span className="game-tab-label">{g.name}</span>
              </button>
            );
          })}
        </div>
        {switching && (
          <div style={{ textAlign: "center", padding: "8px 0 0" }}>
            <div className="spinner" style={{ width: 20, height: 20, margin: "0 auto", borderWidth: 2 }} />
            <div style={{ fontSize: 11, color: theme.accent, marginTop: 4 }}>Загрузка {profile.game_name}...</div>
          </div>
        )}
      </div>

      {/* Roles badges */}
      {!switching && profile.roles && profile.roles.length > 0 && (
        <div className="badge-row fade-in stagger-3">
          {profile.roles.map((r, i) => <span key={i} className="badge-pill">{r}</span>)}
        </div>
      )}

      {/* ── Rank Card ── */}
      {!switching && s && s.rank_name && (
        <div className="section fade-in stagger-3">
          <div className="rank-cards">
            <div className="rank-card" style={{ borderColor: `${theme.accent}33` }}>
              <div className="rank-icon" style={{ animation: "floatY 3s ease-in-out infinite", filter: `drop-shadow(0 0 8px ${theme.glow})` }}>
                {getRankEmoji(s.rank_name)}
              </div>
              <div>
                <div className="rank-label">Ранг</div>
                <div className="rank-value" style={{ color: theme.accent }}>{s.rank_name}</div>
                {s.rank_points != null && (
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{s.rank_points} {getPointsLabel(s.source)}</div>
                )}
              </div>
              <div style={{ marginLeft: "auto", fontSize: 10, color: s.verified ? "var(--accent-green)" : "var(--text-muted)" }}>
                {getSourceLabel(s.source, profile.game_name)}
                {s.verified && " ✓"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Stats Grid ── */}
      {!switching && s && (s.kd != null || s.winrate != null) && (
        <div className="section">
          <h2 className="section-title slide-in-left stagger-4">Статистика</h2>
          <div className="stats-grid">
            {s.kd != null && (
              <div className="stat-card fade-in stagger-4">
                <div className="stat-label">K/D Ratio</div>
                <div className="stat-value">{s.kd.toFixed(2)}</div>
                <ProgressBar percent={Math.min(100, s.kd * 50)} color={s.kd >= 1 ? "green" : "red"} />
              </div>
            )}
            {s.winrate != null && (
              <div className="stat-card fade-in stagger-5">
                <div className="stat-label">Win Rate</div>
                <div className="stat-value">{s.winrate.toFixed(1)}%</div>
                <ProgressBar percent={s.winrate} color={s.winrate >= 50 ? "green" : "red"} />
              </div>
            )}
            {s.unified_score > 0 && (
              <div className="stat-card fade-in stagger-6">
                <div className="stat-label">Unified Score</div>
                <div className="stat-value">{s.unified_score}</div>
                <ProgressBar percent={Math.min(100, s.unified_score / 100)} color="purple" />
              </div>
            )}
          </div>
        </div>
      )}

      {/* No stats message */}
      {!switching && (!s || (s.kd == null && s.winrate == null && !s.rank_name)) && (
        <div className="section fade-in stagger-3">
          <div className="card" style={{ textAlign: "center", padding: 24 }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📊</div>
            <div style={{ fontSize: 14, color: "var(--text-muted)", marginBottom: 12 }}>
              Статистика не загружена. Привяжи аккаунт в настройках и обнови данные.
            </div>
            <button className="btn btn-connect" onClick={handleRefresh} disabled={refreshing}
              style={{ background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}99)` }}>
              {refreshing ? "Обновление..." : "🔄 Обновить статистику"}
            </button>
          </div>
        </div>
      )}

      {/* Refresh button */}
      {!switching && s && s.rank_name && (
        <div className="section fade-in stagger-7" style={{ textAlign: "center" }}>
          <button className="btn btn-connect" onClick={handleRefresh} disabled={refreshing}
            style={{ background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}99)`, opacity: refreshing ? 0.6 : 1 }}>
            {refreshing ? "⏳ Обновление..." : "🔄 Обновить статистику"}
          </button>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 6 }}>
            Источник: {getSourceLabel(s.source, profile.game_name)} • {s.source_status}
          </div>
        </div>
      )}
    </main>
  );
}
