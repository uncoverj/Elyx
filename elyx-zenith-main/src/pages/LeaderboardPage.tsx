import { PageShell, SectionTitle } from "@/components/elyx/PageShell";
import { leaderboardPlayers, rankDistribution } from "@/lib/mock-data";
import { motion } from "framer-motion";
import { Trophy, ChevronDown, Users, Medal, Crown } from "lucide-react";
import { useState } from "react";

const tierColors: Record<string, string> = {
  Radiant: "text-warning",
  "Immortal 3": "text-primary",
  "Immortal 2": "text-primary",
  "Immortal 1": "text-primary",
};

const tierBadges: Record<string, string> = {
  Radiant: "bg-warning/10 text-warning border-warning/20",
  "Immortal 3": "bg-primary/10 text-primary border-primary/20",
  "Immortal 2": "bg-primary/10 text-primary border-primary/20",
  "Immortal 1": "bg-primary/10 text-primary border-primary/20",
};

export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<"rating" | "trust">("rating");

  const sorted = [...leaderboardPlayers].sort((a, b) =>
    sortBy === "rating" ? b.rating - a.rating : b.trust - a.trust
  );

  return (
    <PageShell>
      <div className="px-4 md:px-6 pt-6 lg:pt-0 max-w-5xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <SectionTitle
              icon={<Crown size={20} className="text-primary" />}
              title="Лидеры"
              subtitle="12,689 Пользователей зарегистрировано"
            />
          </div>
        </div>

        {/* Sort */}
        <button
          onClick={() => setSortBy(sortBy === "rating" ? "trust" : "rating")}
          className="pill-active flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all"
        >
          {sortBy === "rating" ? "Игровой ранг" : "Elyx Trust"}
          <ChevronDown size={14} />
        </button>

        {/* Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card-static rounded-2xl p-5 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/[0.03] via-transparent to-accent/[0.03]" />
          <div className="flex h-24 gap-1.5 items-end relative z-10">
            {rankDistribution.map((r, i) => (
              <motion.div
                key={r.rank}
                initial={{ height: 0 }}
                animate={{ height: `${Math.max(r.pct * 8, 5)}%` }}
                transition={{ delay: 0.1 + i * 0.06, duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                className="flex-1 rounded-t-md bg-primary/40 hover:bg-primary/60 transition-colors cursor-pointer"
              />
            ))}
          </div>
          <div className="flex gap-1.5 mt-2 relative z-10">
            {rankDistribution.map((r) => (
              <span key={r.rank} className="flex-1 text-center text-[9px] text-muted-foreground font-medium">{r.rank}</span>
            ))}
          </div>
        </motion.div>

        {/* Leaderboard */}
        <div className="glass-card-static rounded-2xl overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[2rem_1fr_5rem_3.5rem_5rem] md:grid-cols-[3rem_1fr_6rem_5rem_7rem] gap-2 px-4 py-3 border-b border-border/80">
            <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold">#</span>
            <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold">Игрок</span>
            <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold text-right">Trust</span>
            <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold text-right">Рейтинг</span>
            <span className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold text-right">Тир</span>
          </div>

          {/* Rows */}
          {sorted.map((player, i) => {
            const badge = tierBadges[player.tier] || "bg-secondary text-foreground border-border/50";
            const isTop3 = i < 3;
            return (
              <motion.div
                key={player.rank}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 + i * 0.03, ease: [0.4, 0, 0.2, 1] }}
                className={`grid grid-cols-[2rem_1fr_5rem_3.5rem_5rem] md:grid-cols-[3rem_1fr_6rem_5rem_7rem] gap-2 px-4 py-3.5 border-b border-border/30 hover:bg-card-hover transition-all duration-200 items-center ${isTop3 ? "bg-primary/[0.02]" : ""}`}
              >
                <span className={`font-display font-bold text-sm tabular-nums ${isTop3 ? "text-primary" : "text-muted-foreground"}`}>
                  {isTop3 && i === 0 ? "👑" : player.rank}
                </span>
                <div className="flex items-center gap-2 min-w-0">
                  <div className={`w-7 h-7 rounded-lg ${isTop3 ? "bg-primary/10 border border-primary/20" : "bg-secondary"} flex items-center justify-center shrink-0`}>
                    <span className="text-[9px] font-bold font-display">{player.username.slice(0, 2)}</span>
                  </div>
                  <span className={`font-medium text-sm truncate ${isTop3 ? "text-foreground" : ""}`}>
                    {player.username}
                  </span>
                </div>
                <span className="text-right text-xs text-muted-foreground font-mono tabular-nums">
                  {player.trust.toFixed(1)}%
                </span>
                <span className="text-right font-display font-bold text-sm tabular-nums">
                  {player.rating.toLocaleString()}
                </span>
                <div className="flex justify-end">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badge}`}>
                    {player.tier}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </PageShell>
  );
}
