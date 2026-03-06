"use client";

import { useMemo, useState } from "react";

import { SkeletonProfile } from "@/components/skeleton";
import { useProfile } from "@/lib/use-profile";

type Theme = {
  accent: string;
  accentSoft: string;
  border: string;
  hero: string;
};

const GAME_THEMES: Record<string, Theme> = {
  Valorant: {
    accent: "#ff4d67",
    accentSoft: "rgba(255,77,103,0.2)",
    border: "rgba(255,77,103,0.35)",
    hero:
      "radial-gradient(110% 130% at 0% 0%, rgba(255,77,103,0.45) 0%, rgba(255,77,103,0.1) 28%, transparent 68%), linear-gradient(180deg, rgba(10,16,40,0.35) 0%, #090f2a 88%)",
  },
  CS2: {
    accent: "#f0a23c",
    accentSoft: "rgba(240,162,60,0.2)",
    border: "rgba(240,162,60,0.35)",
    hero:
      "radial-gradient(110% 130% at 0% 0%, rgba(240,162,60,0.4) 0%, rgba(240,162,60,0.1) 30%, transparent 68%), linear-gradient(180deg, rgba(10,16,40,0.35) 0%, #090f2a 88%)",
  },
};

const DEFAULT_THEME: Theme = {
  accent: "#7b8cff",
  accentSoft: "rgba(123,140,255,0.2)",
  border: "rgba(123,140,255,0.35)",
  hero:
    "radial-gradient(110% 130% at 0% 0%, rgba(123,140,255,0.4) 0%, rgba(123,140,255,0.1) 30%, transparent 68%), linear-gradient(180deg, rgba(10,16,40,0.35) 0%, #090f2a 88%)",
};

const VAL_RANKS = [
  "Iron 1",
  "Iron 2",
  "Iron 3",
  "Bronze 1",
  "Bronze 2",
  "Bronze 3",
  "Silver 1",
  "Silver 2",
  "Silver 3",
  "Gold 1",
  "Gold 2",
  "Gold 3",
  "Platinum 1",
  "Platinum 2",
  "Platinum 3",
  "Diamond 1",
  "Diamond 2",
  "Diamond 3",
  "Ascendant 1",
  "Ascendant 2",
  "Ascendant 3",
  "Immortal 1",
  "Immortal 2",
  "Immortal 3",
  "Radiant",
];

function estimatePeakRank(currentRank: string | null): string | null {
  if (!currentRank) return null;
  const normalized = currentRank.trim();
  const idx = VAL_RANKS.findIndex((r) => r.toLowerCase() === normalized.toLowerCase());
  if (idx < 0) return currentRank;
  return VAL_RANKS[Math.min(idx + 2, VAL_RANKS.length - 1)];
}

function toPercent(value: number | null | undefined, fallback = "N/A"): string {
  if (value == null) return fallback;
  return `${value.toFixed(1)}%`;
}

function toFixed(value: number | null | undefined, digits = 2, fallback = "N/A"): string {
  if (value == null) return fallback;
  return value.toFixed(digits);
}

function getTierHint(score: number): string {
  if (score >= 8500) return "Elite tier";
  if (score >= 6500) return "High tier";
  if (score >= 4500) return "Mid tier";
  if (score > 0) return "Entry tier";
  return "Unrated";
}

function TelegramBadge({ username }: { username: string | null | undefined }) {
  return (
    <div className="tg-badge">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M21.4 4.6a1.8 1.8 0 0 0-1.9-.3L3 10.7a1.7 1.7 0 0 0 .1 3.2l3.7 1.2 1.4 4.2a1.7 1.7 0 0 0 3 .5l2.1-2.6 3.8 2.8a1.8 1.8 0 0 0 2.8-1l2.3-12.7a1.8 1.8 0 0 0-.8-1.7Zm-4.1 3.3-7.7 6.9a.8.8 0 0 0-.3.6l-.2 2.3-.8-2.4a.8.8 0 0 0-.5-.5l-2.4-.8 12-4.8Z"
        />
      </svg>
      <span>{username ? `@${username}` : "Telegram connected"}</span>
    </div>
  );
}

export default function ProfilePage() {
  const { profile, accounts, games, loading, error, refreshStats, switchGame } = useProfile();
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null);

  const handleRefresh = async () => {
    setRefreshing(true);
    setRefreshMessage(null);
    const result = await refreshStats();
    setRefreshing(false);
    if (result.ok) {
      setRefreshMessage("Stats refreshed");
      return;
    }
    setRefreshMessage(result.error || "Refresh failed");
  };

  if (loading) {
    return (
      <main>
        <SkeletonProfile />
      </main>
    );
  }

  if (!profile) {
    return (
      <main>
        <div className="loading-screen">
          <div className="loading-logo">ELYX</div>
          <p style={{ color: "var(--text-secondary)", fontSize: 13, textAlign: "center", padding: "0 32px" }}>
            {error ?? "Profile not found. Open bot in Telegram and complete registration."}
          </p>
        </div>
      </main>
    );
  }

  const stats = profile.stats;
  const theme = GAME_THEMES[profile.game_name] ?? DEFAULT_THEME;
  const riot = accounts.find((a) => a.provider === "riot");
  const peakRank = estimatePeakRank(stats?.rank_name ?? null);
  const trustVotes = (profile.trust_up ?? 0) + (profile.trust_down ?? 0);
  const trustPercent = trustVotes > 0 ? Math.round((profile.trust_up / trustVotes) * 100) : 100;
  const score = stats?.unified_score ?? 0;

  const orderedGames = useMemo(() => [...games].sort((a, b) => a.name.localeCompare(b.name)), [games]);

  const overviewCards = [
    {
      label: "K/D Ratio",
      value: toFixed(stats?.kd, 2),
      note: stats?.kd != null ? (stats.kd >= 1 ? "Strong impact" : "Improve survivability") : "No data",
    },
    {
      label: "Win Rate",
      value: toPercent(stats?.winrate),
      note: stats?.winrate != null ? (stats.winrate >= 55 ? "Top performance" : "Can be improved") : "No data",
    },
    {
      label: "Elyx Score",
      value: `${score}`,
      note: getTierHint(score),
    },
    {
      label: "Trust",
      value: `${trustPercent}%`,
      note: `${profile.trust_up} up / ${profile.trust_down} down`,
    },
  ];

  return (
    <main className="fade-in">
      <section className="valo-hero" style={{ background: theme.hero, borderBottomColor: theme.border }}>
        <span className="hero-elyx-logo">ELYX</span>

        <div className="valo-head">
          <div className="valo-avatar" style={{ borderColor: theme.border }}>
            {profile.nickname.slice(0, 1).toUpperCase()}
          </div>

          <div className="valo-main">
            <div className="valo-nickname-row">
              <h1>{profile.nickname}</h1>
              {profile.is_premium ? <span className="valo-premium">PREMIUM</span> : null}
            </div>
            <TelegramBadge username={profile.username} />
          </div>

          <button className="valo-refresh-btn" onClick={handleRefresh} disabled={refreshing}>
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        <div className="valo-stat-strip">
          <div>
            <strong>{profile.game_name}</strong>
            <span>Main game</span>
          </div>
          <div>
            <strong>{trustPercent}%</strong>
            <span>Trust</span>
          </div>
          <div>
            <strong>{score}</strong>
            <span>Score</span>
          </div>
        </div>
      </section>

      <section className="valo-page">
        <div className="valo-dashboard">
          <div className="valo-main-col">
            <div className="valo-chip-row">
              <span className="valo-chip" style={{ borderColor: theme.border, color: theme.accent }}>
                Competitive
              </span>
              <span className="valo-chip">Season E26:A1</span>
              <span className="valo-chip">{stats?.verified ? "Verified" : "Unverified"}</span>
            </div>

            <div className="valo-rank-panels">
              <article className="valo-rank-card">
                <p>Current rank</p>
                <h3>{stats?.rank_name ?? "Unranked"}</h3>
                <span>{stats?.rank_points != null ? `${stats.rank_points} points` : "No points yet"}</span>
              </article>
              <article className="valo-rank-card">
                <p>Peak rank</p>
                <h3>{peakRank ?? "Unknown"}</h3>
                <span>{score > 0 ? "Estimated from current progression" : "Play ranked to unlock"}</span>
              </article>
            </div>

            <h2 className="valo-section-title">Overview</h2>
            <div className="valo-overview-grid">
              {overviewCards.map((card) => (
                <article key={card.label} className="valo-overview-card">
                  <p>{card.label}</p>
                  <h4>{card.value}</h4>
                  <span>{card.note}</span>
                </article>
              ))}
            </div>
          </div>

          <aside className="valo-side-col">
            <h2 className="valo-section-title">Account status</h2>
            <div className="desktop-card">
              <div className="desktop-kv">
                <span>Telegram</span>
                <strong>{profile.tg_id ? "Connected" : "Missing"}</strong>
              </div>
              <div className="desktop-kv">
                <span>Riot ID</span>
                <strong>{riot?.connected ? riot.account_ref : "Not linked"}</strong>
              </div>
              <div className="desktop-kv">
                <span>Stats provider</span>
                <strong>{stats?.source ?? "N/A"}</strong>
              </div>
              <div className="desktop-kv">
                <span>Data status</span>
                <strong>{stats?.source_status ?? "N/A"}</strong>
              </div>
            </div>

            <h2 className="valo-section-title">Switch game</h2>
            <div className="game-pills" style={{ paddingLeft: 0, paddingRight: 0 }}>
              {orderedGames.map((g) => (
                <button
                  key={g.id}
                  className={`game-pill${profile.game_id === g.id ? " active" : ""}`}
                  onClick={() => switchGame(g.id)}
                >
                  {g.name}
                </button>
              ))}
            </div>

            {refreshMessage ? <p className="valo-note">{refreshMessage}</p> : null}
          </aside>
        </div>
      </section>
    </main>
  );
}
