"use client";

import { useEffect, useState } from "react";
import WebAppInit from "@/components/webapp-init";
import { useProfile } from "@/lib/use-profile";
import { SkeletonProfile } from "@/components/skeleton";

const GAME_THEMES: Record<string, { accent: string; glow: string; gradient: string }> = {
  "Valorant": { accent: "#FF4655", glow: "rgba(255,70,85,0.2)", gradient: "linear-gradient(180deg, rgba(255,70,85,0.18) 0%, transparent 60%)" },
  "CS2": { accent: "#DE9B35", glow: "rgba(222,155,53,0.2)", gradient: "linear-gradient(180deg, rgba(222,155,53,0.18) 0%, transparent 60%)" },
  "League of Legends": { accent: "#C89B3C", glow: "rgba(200,155,60,0.2)", gradient: "linear-gradient(180deg, rgba(200,155,60,0.18) 0%, transparent 60%)" },
  "Dota 2": { accent: "#E44D2E", glow: "rgba(228,77,46,0.2)", gradient: "linear-gradient(180deg, rgba(228,77,46,0.18) 0%, transparent 60%)" },
  "Apex Legends": { accent: "#CD3333", glow: "rgba(205,51,51,0.2)", gradient: "linear-gradient(180deg, rgba(205,51,51,0.18) 0%, transparent 60%)" },
  "Overwatch 2": { accent: "#FA9C1E", glow: "rgba(250,156,30,0.2)", gradient: "linear-gradient(180deg, rgba(250,156,30,0.18) 0%, transparent 60%)" },
  "Fortnite": { accent: "#9D4DBB", glow: "rgba(157,77,187,0.2)", gradient: "linear-gradient(180deg, rgba(157,77,187,0.18) 0%, transparent 60%)" },
};
const DEFAULT_THEME = { accent: "#7B2FBE", glow: "rgba(123,47,190,0.2)", gradient: "linear-gradient(180deg, rgba(123,47,190,0.18) 0%, transparent 60%)" };

function getRankEmoji(rank: string | null) {
  if (!rank) return "🎮";
  const r = rank.toLowerCase();
  if (r.includes("iron")) return "⚫";
  if (r.includes("bronze")) return "🟤";
  if (r.includes("silver")) return "⚪";
  if (r.includes("gold")) return "🟡";
  if (r.includes("platinum")) return "🩵";
  if (r.includes("diamond")) return "💎";
  if (r.includes("ascendant")) return "💚";
  if (r.includes("immortal")) return "🔴";
  if (r.includes("radiant")) return "🌟";
  if (r.includes("level 1") || r.includes("level 2")) return "⚪";
  if (r.includes("level 3") || r.includes("level 4")) return "🟤";
  if (r.includes("level 5") || r.includes("level 6")) return "🟡";
  if (r.includes("level 7") || r.includes("level 8")) return "💎";
  if (r.includes("level 9") || r.includes("level 10")) return "🟣";
  return "🎮";
}

interface StatCardProps {
  title: string;
  value: string;
  percentile?: string;
  positive?: boolean;
}

function StatCard({ title, value, percentile, positive }: StatCardProps) {
  const [width, setWidth] = useState(0);
  const pctNum = percentile ? parseInt(percentile.replace(/\D+/g, "")) : 50;
  const fill = positive ? 100 - pctNum : pctNum;

  useEffect(() => {
    const t = setTimeout(() => setWidth(Math.max(5, Math.min(100, fill))), 120);
    return () => clearTimeout(t);
  }, [fill]);

  return (
    <div className={`stat-card ${positive ? "stat-positive" : "stat-negative"}`}>
      <p className="stat-card-label">{title}</p>
      <p className="stat-card-value">{value}</p>
      {percentile && <p className="stat-card-pct">{percentile}</p>}
      <div className="stat-card-bar">
        <div className="stat-card-fill" style={{ width: `${width}%` }}>
          <div className="stat-card-dot" />
        </div>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  const { profile, loading, error, refreshStats, games, switchGame } = useProfile();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    const result = await refreshStats();
    setRefreshing(false);
    if (!result.ok && result.error === "no_match_history") {
      alert("⚠️ Аккаунт найден, но нет сыгранных матчей. Сыграй хотя бы одну игру!");
    }
  };

  const theme = GAME_THEMES[profile?.game_name ?? ""] ?? DEFAULT_THEME;

  if (loading) return (
    <main><WebAppInit /><SkeletonProfile /></main>
  );

  if (!profile) return (
    <main>
      <WebAppInit />
      <div className="loading-screen">
        <div className="loading-logo">ELYX</div>
        <p style={{ color: "var(--text-secondary)", fontSize: 13, textAlign: "center", padding: "0 32px" }}>
          {error ?? "Профиль не найден. Зарегистрируйся через бота в Telegram."}
        </p>
      </div>
    </main>
  );

  const s = profile.stats;
  const kd = s?.kd != null ? s.kd.toFixed(2) : "—";
  const wr = s?.winrate != null ? `${s.winrate.toFixed(1)}%` : "—";
  const rank = s?.rank_name ?? "Unranked";
  const rankEmoji = getRankEmoji(s?.rank_name ?? null);

  const trustTotal = (profile.trust_up ?? 0) + (profile.trust_down ?? 0);
  const trustPct = trustTotal > 0 ? Math.round((profile.trust_up / trustTotal) * 100) : 100;

  // Stats slots
  const statsCards = [
    { title: "K/D Ratio", value: kd, percentile: s?.kd ? (s.kd > 1.2 ? "Top 30%" : "Bottom 40%") : undefined, positive: (s?.kd ?? 0) > 1.1 },
    { title: "Win Rate", value: wr, percentile: s?.winrate ? (s.winrate > 55 ? "Top 20%" : "Bottom 45%") : undefined, positive: (s?.winrate ?? 0) > 52 },
    { title: "Trust Score", value: `${trustPct}%`, percentile: `${trustPct} pts`, positive: trustPct > 70 },
    { title: "Unified Score", value: `${s?.unified_score ?? 0}`, percentile: s?.rank_name ? "Rated" : "Not rated", positive: (s?.unified_score ?? 0) > 4000 },
  ];

  return (
    <main className="fade-in">
      <WebAppInit />

      {/* ── Hero Banner ─────────────────────────────── */}
      <div className="hero-banner" style={{ background: theme.gradient }}>
        <div
          style={{
            position: "absolute", inset: 0,
            background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)"
          }}
        />
        {/* ELYX logo */}
        <span className="hero-elyx-logo">ELYX</span>

        <div className="hero-content">
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            {/* Avatar */}
            <div className="avatar-wrap">
              <div className="avatar-glow" style={{ background: theme.glow }} />
              <div className="avatar" style={{
                width: 52, height: 52,
                background: `linear-gradient(135deg, ${theme.accent}33, var(--bg-card))`,
                border: `2px solid ${theme.accent}50`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 22
              }}>
                {profile.game_name[0] ?? "?"}
              </div>
            </div>

            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
                <span style={{ fontWeight: 800, fontSize: 17, color: "var(--text-primary)" }}>
                  {profile.nickname}
                </span>
                {profile.is_premium && <span style={{ color: "#F0A500" }}>⭐</span>}
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>👍 {profile.trust_up}</span>
                <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>👎 {profile.trust_down}</span>
                <span style={{ fontSize: 12, color: theme.accent }}>{profile.game_name}</span>
              </div>
            </div>
          </div>

          {/* Rank */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="rank-badge" style={{
              background: `${theme.accent}1A`,
              borderColor: `${theme.accent}40`,
              color: theme.accent
            }}>
              {rankEmoji} {rank}
            </span>
            {s?.rank_points && (
              <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                {s.rank_points} pts
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ── Game Switcher ─────────────────────────── */}
      {games.length > 0 && (
        <div style={{ padding: "12px 0 0" }}>
          <div className="section-hd">
            <span className="section-title">Текущая игра</span>
          </div>
          <div className="game-pills">
            {games.map(g => (
              <button
                key={g.id}
                className={`game-pill${profile.game_id === g.id ? " active" : ""}`}
                onClick={() => switchGame(g.id)}
              >
                {g.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Stat Cards 2×2 ────────────────────────── */}
      <div className="section-hd">
        <span className="section-title">Статистика</span>
        <button onClick={handleRefresh} disabled={refreshing}
          style={{ fontSize: 12, color: theme.accent, fontWeight: 600, background: "none", border: "none", cursor: "pointer" }}>
          {refreshing ? "⏳" : "↻ Обновить"}
        </button>
      </div>

      <div className="card-grid-2">
        {statsCards.map(sc => (
          <StatCard key={sc.title} {...sc} />
        ))}
      </div>

      {/* ── Bottom summary ────────────────────────── */}
      <div style={{ margin: "0 16px 24px" }}>
        <div className="card" style={{ padding: "14px 16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 0 }}>
            {[
              { label: "Роли", value: profile.roles?.join(", ") || "—", color: theme.accent },
              { label: "Теги", value: profile.tags?.slice(0, 2).join(", ") || "—", color: "var(--text-primary)" },
              { label: "Возраст", value: profile.age?.toString() ?? "—", color: "var(--text-primary)" },
            ].map((item, i) => (
              <div key={i} style={{
                textAlign: "center",
                padding: "0 8px",
                borderLeft: i > 0 ? "1px solid var(--border-subtle)" : "none"
              }}>
                <p style={{ fontSize: 10, color: "var(--text-secondary)", marginBottom: 4 }}>{item.label}</p>
                <p style={{ fontSize: 13, fontWeight: 700, color: item.color, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
