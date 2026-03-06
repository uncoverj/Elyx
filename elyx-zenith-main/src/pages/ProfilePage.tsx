import { HeroHeader } from "@/components/elyx/HeroHeader";
import { RankCard } from "@/components/elyx/RankCard";
import { StatCard } from "@/components/elyx/StatCard";
import { PageShell, SectionTitle } from "@/components/elyx/PageShell";
import { useElyx } from "@/context/ElyxContext";
import { motion } from "framer-motion";
import { RefreshCw, Activity, Award, Target } from "lucide-react";
import { toast } from "@/components/ui/sonner";
import { useMemo, useState } from "react";

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function parseRank(rankName: string | null | undefined): { tier: string; division: number } {
  if (!rankName) return { tier: "Unranked", division: 1 };
  const normalized = rankName.trim();
  const match = normalized.match(/^([A-Za-z]+)\s*(\d+)?/);
  if (!match) return { tier: normalized, division: 1 };
  return {
    tier: match[1],
    division: match[2] ? Number(match[2]) : 1,
  };
}

export default function ProfilePage() {
  const { profile, games, loading, error, refreshStats, switchGame } = useElyx();
  const [refreshing, setRefreshing] = useState(false);
  const [switchingGame, setSwitchingGame] = useState<number | null>(null);

  const gamePills = useMemo(
    () =>
      games.map((g) => ({
        id: g.id,
        name: g.name,
        active: profile?.game_id === g.id,
      })),
    [games, profile?.game_id]
  );

  if (loading) {
    return (
      <PageShell>
        <div className="px-4 md:px-6 pt-8 max-w-5xl mx-auto">
          <div className="glass-card-static rounded-2xl p-6">
            <p className="text-sm text-muted-foreground">Loading profile...</p>
          </div>
        </div>
      </PageShell>
    );
  }

  if (!profile) {
    return (
      <PageShell>
        <div className="px-4 md:px-6 pt-8 max-w-5xl mx-auto">
          <div className="glass-card-static rounded-2xl p-6">
            <h1 className="font-display font-bold text-xl">Profile not found</h1>
            <p className="text-sm text-muted-foreground mt-2">
              {error || "Open Elyx from Telegram Mini App so the backend can authenticate your account."}
            </p>
          </div>
        </div>
      </PageShell>
    );
  }

  const stats = profile.stats;
  const trustPercent = (profile.trust_score <= 1 ? profile.trust_score * 100 : profile.trust_score);
  const currentRank = parseRank(stats?.rank_name);

  const scoreFromRank = stats?.rank_points != null ? clamp(Math.round((stats.rank_points / 9000) * 100), 1, 100) : 1;
  const scorePercentile = stats?.unified_score != null ? clamp(Math.round(stats.unified_score / 100), 1, 100) : 1;

  const statCards = [
    {
      label: "K/D Ratio",
      value: stats?.kd != null ? stats.kd.toFixed(2) : "—",
      percentile: stats?.kd != null ? clamp(Math.round((stats.kd / 2.0) * 100), 1, 100) : 1,
    },
    {
      label: "Win %",
      value: stats?.winrate != null ? `${stats.winrate.toFixed(1)}%` : "—",
      percentile: stats?.winrate != null ? clamp(Math.round(stats.winrate), 1, 100) : 1,
    },
    {
      label: "Rank Power",
      value: stats?.rank_points != null ? `${stats.rank_points}` : "—",
      percentile: scoreFromRank,
    },
    {
      label: "Elyx Trust",
      value: `${trustPercent.toFixed(1)}%`,
      percentile: clamp(Math.round(trustPercent), 1, 100),
    },
  ];

  const compactCards = [
    {
      label: "Elyx Score",
      value: stats?.unified_score != null ? stats.unified_score.toLocaleString() : "0",
      percentile: scorePercentile,
    },
    {
      label: "Likes",
      value: profile.trust_up,
      percentile: clamp(profile.trust_up + 5, 1, 100),
    },
    {
      label: "Dislikes",
      value: profile.trust_down,
      percentile: clamp(100 - profile.trust_down * 2, 1, 100),
    },
    {
      label: "Verified",
      value: stats?.verified ? "Yes" : "No",
      percentile: stats?.verified ? 95 : 25,
    },
  ];

  const handleRefresh = async () => {
    setRefreshing(true);
    const result = await refreshStats();
    setRefreshing(false);
    if (result.ok) {
      toast.success("Stats updated successfully");
      return;
    }
    toast.error(result.error || "Could not refresh stats");
  };

  const handleSwitchGame = async (gameId: number) => {
    setSwitchingGame(gameId);
    const result = await switchGame(gameId);
    setSwitchingGame(null);
    if (result.ok) {
      toast.success("Game switched");
      return;
    }
    toast.error(result.error || "Could not switch game");
  };

  return (
    <PageShell>
      <HeroHeader profile={profile} />

      <div className="px-4 md:px-6 mt-6 space-y-6 max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center justify-between gap-2 flex-wrap"
        >
          <div className="flex gap-2 overflow-x-auto no-scrollbar">
            {gamePills.map((g) => (
              <button
                key={g.id}
                onClick={() => handleSwitchGame(g.id)}
                disabled={switchingGame === g.id}
                className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all duration-200 ${
                  g.active ? "pill-active" : "pill-inactive"
                } ${switchingGame === g.id ? "opacity-60" : ""}`}
              >
                {g.name}
              </button>
            ))}
            <button className="px-3 py-2 rounded-xl text-xs font-bold pill-inactive flex items-center gap-1">
              Live data
              <span className="w-1 h-1 rounded-full bg-success" />
            </button>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-secondary border border-border/50 text-xs font-bold text-muted-foreground hover:text-foreground hover:border-border transition-all duration-200 focus-ring disabled:opacity-50"
            aria-label="Refresh stats"
          >
            <RefreshCw size={13} className={refreshing ? "animate-spin" : ""} />
            {refreshing ? "Updating..." : "Refresh"}
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex gap-3 mb-3">
            <span className="text-sm font-display font-bold text-foreground">Current rank</span>
            <span className="text-sm font-display font-bold text-primary">Peak rank</span>
          </div>
          <div className="flex gap-3">
            <RankCard type="current" tier={currentRank.tier} division={currentRank.division} rr={stats?.rank_points ?? undefined} />
            <RankCard
              type="peak"
              tier={currentRank.tier}
              division={Math.min(currentRank.division + 1, 3)}
              rr={stats?.rank_points != null ? stats.rank_points + 50 : undefined}
            />
          </div>
        </motion.div>

        <div>
          <SectionTitle
            icon={<Activity size={18} className="text-primary" />}
            title="Overview"
            subtitle={`${profile.game_name} • ${profile.roles?.join(", ") || "No role data"}`}
          />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
            {statCards.map((card, idx) => (
              <StatCard
                key={card.label}
                label={card.label}
                value={card.value}
                percentile={card.percentile}
                delay={idx * 0.05}
              />
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {compactCards.map((card, idx) => (
            <StatCard
              key={card.label}
              label={card.label}
              value={card.value}
              percentile={card.percentile}
              delay={0.2 + idx * 0.05}
              size="sm"
            />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="glass-card-static rounded-2xl p-6 gradient-border relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/[0.04] via-transparent to-accent/[0.04]" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Award size={16} className="text-primary" />
                <p className="text-[11px] text-muted-foreground font-bold uppercase tracking-wider">Elyx Score</p>
              </div>
              <p className="text-4xl font-display font-bold gradient-text tracking-tight">{(stats?.unified_score ?? 0).toLocaleString()}</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 mb-1 justify-end">
                <Target size={16} className="text-success" />
                <p className="text-[11px] text-muted-foreground font-bold uppercase tracking-wider">Trust</p>
              </div>
              <p className="text-4xl font-display font-bold text-success tracking-tight">{trustPercent.toFixed(1)}%</p>
            </div>
          </div>

          <div className="mt-4 relative z-10">
            <div className="stat-bar-thick">
              <motion.div
                className="stat-bar-fill bg-success"
                initial={{ width: 0 }}
                animate={{ width: `${clamp(Math.round(trustPercent), 1, 100)}%` }}
                transition={{ delay: 0.5, duration: 1.0, ease: [0.4, 0, 0.2, 1] }}
              />
            </div>
          </div>
        </motion.div>
      </div>
    </PageShell>
  );
}
