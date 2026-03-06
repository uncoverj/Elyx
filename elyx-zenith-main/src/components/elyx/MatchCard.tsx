import { motion } from "framer-motion";
import type { MatchData } from "@/lib/mock-data";
import { Swords, ChevronRight } from "lucide-react";

interface MatchCardProps {
  match: MatchData;
  index: number;
}

const agentInitials: Record<string, { bg: string }> = {
  Jett: { bg: "bg-neon-blue/20 text-neon-blue" },
  Neon: { bg: "bg-warning/20 text-warning" },
  Brimstone: { bg: "bg-primary/20 text-primary" },
  Omen: { bg: "bg-neon-purple/20 text-neon-purple" },
  Pearl: { bg: "bg-success/20 text-success" },
};

export function MatchCard({ match, index }: MatchCardProps) {
  const agent = agentInitials[match.agent] || { bg: "bg-secondary text-foreground" };

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04, duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
      className={`glass-card rounded-xl overflow-hidden ${match.won ? "win-card" : "loss-card"} group cursor-pointer`}
    >
      <div className="p-3.5 md:p-4 flex items-center justify-between gap-3">
        {/* Left: Agent + score */}
        <div className="flex items-center gap-3 min-w-0">
          <div className={`w-10 h-10 md:w-11 md:h-11 rounded-xl flex items-center justify-center shrink-0 ${agent.bg} font-display font-bold text-xs`}>
            {match.agent.slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className={`text-lg md:text-xl font-display font-bold tabular-nums ${match.won ? "text-success" : "text-destructive"}`}>
                {match.score}
              </span>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${match.won ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"}`}>
                {match.won ? "WIN" : "LOSS"}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
              <span className="font-medium">KDA <span className="text-foreground/70">{match.kda}</span></span>
              <span className="w-px h-3 bg-border" />
              <span className="font-medium">КД <span className="text-foreground/70 font-mono">{match.kd.toFixed(2)}</span></span>
              <span className="w-px h-3 bg-border" />
              <span className="font-medium">У/Р <span className="text-foreground/70 font-mono">{match.damagePerRound}</span></span>
            </div>
          </div>
        </div>

        {/* Right: Map + mode */}
        <div className="text-right shrink-0 flex items-center gap-2">
          <div>
            <p className="text-sm font-display font-bold">{match.map}</p>
            <p className="text-[10px] text-muted-foreground font-medium">{match.mode}</p>
          </div>
          <ChevronRight size={16} className="text-muted-foreground/30 group-hover:text-muted-foreground/60 transition-colors" />
        </div>
      </div>
    </motion.div>
  );
}
