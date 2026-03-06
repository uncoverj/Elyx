import { motion } from "framer-motion";
import { Star, TrendingUp, ChevronUp } from "lucide-react";

interface RankCardProps {
  type: "current" | "peak";
  tier: string;
  division: number;
  rr?: number;
}

const rankColors: Record<string, string> = {
  Iron: "text-muted-foreground",
  Bronze: "text-warning",
  Silver: "text-muted-foreground",
  Gold: "text-warning",
  Platinum: "text-neon-blue",
  Diamond: "text-neon-purple",
  Ascendant: "text-success",
  Immortal: "text-primary",
  Radiant: "text-warning",
};

const rankGlow: Record<string, string> = {
  Diamond: "glow-purple",
  Ascendant: "glow-success",
  Immortal: "glow-red",
  Radiant: "glow-red",
};

export function RankCard({ type, tier, division, rr }: RankCardProps) {
  const isPeak = type === "peak";
  const color = rankColors[tier] || "text-foreground";
  const glow = rankGlow[tier] || "";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.93 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={`glass-card rounded-xl p-4 flex items-center gap-3 flex-1 min-w-[140px] relative overflow-hidden ${glow}`}
    >
      {/* Decorative gradient */}
      <div className={`absolute inset-0 opacity-[0.04] ${isPeak ? "bg-gradient-to-br from-accent to-transparent" : "bg-gradient-to-br from-primary to-transparent"}`} />
      
      <div className={`w-11 h-11 rounded-xl bg-secondary/80 flex items-center justify-center ${color} relative z-10 border border-border/50`}>
        {isPeak ? <TrendingUp size={20} strokeWidth={2.5} /> : <Star size={20} strokeWidth={2.5} />}
      </div>
      <div className="relative z-10">
        <p className="text-[10px] uppercase tracking-[0.1em] text-muted-foreground font-bold">
          {isPeak ? "Peak Rank" : "Current Rating"}
        </p>
        <p className={`font-display font-bold text-lg leading-tight ${color}`}>
          {tier} {division}
        </p>
        {rr !== undefined && (
          <div className="flex items-center gap-0.5 mt-0.5">
            <ChevronUp size={10} className="text-success" />
            <p className="text-[10px] text-muted-foreground font-medium">{rr} RR</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
