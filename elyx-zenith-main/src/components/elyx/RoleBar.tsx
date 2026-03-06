import { motion } from "framer-motion";

interface RoleBarProps {
  name: string;
  matches: number;
  winRate: number;
  kd: number;
  damagePerRound: number;
  totalMatches: number;
  index: number;
}

const roleColors: Record<string, string> = {
  Duelist: "bg-primary",
  Controller: "bg-neon-blue",
  Initiator: "bg-success",
  Sentinel: "bg-neon-purple",
};

const roleGradients: Record<string, string> = {
  Duelist: "from-primary/10 to-transparent",
  Controller: "from-neon-blue/10 to-transparent",
  Initiator: "from-success/10 to-transparent",
  Sentinel: "from-neon-purple/10 to-transparent",
};

export function RoleBar({ name, matches, winRate, kd, damagePerRound, totalMatches, index }: RoleBarProps) {
  const pct = Math.round((matches / totalMatches) * 100);
  const wins = Math.round(matches * winRate / 100);
  const losses = matches - wins;
  const barColor = roleColors[name] || "bg-primary";
  const gradient = roleGradients[name] || "from-primary/10 to-transparent";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, ease: [0.4, 0, 0.2, 1] }}
      className="glass-card rounded-xl p-4 relative overflow-hidden"
    >
      <div className={`absolute inset-0 bg-gradient-to-r ${gradient} opacity-50`} />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="font-display font-bold text-sm">{name}</p>
            <p className="text-[11px] text-muted-foreground">
              {matches} played · K/D <span className="text-foreground/70 font-mono">{kd.toFixed(2)}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="font-display font-bold text-primary text-xl tabular-nums">{pct}%</p>
            <p className="text-[10px] text-muted-foreground font-medium">
              <span className="text-success">{wins}W</span> <span className="text-destructive">{losses}L</span>
            </p>
          </div>
        </div>
        <div className="stat-bar-thick">
          <motion.div
            className={`stat-bar-fill ${barColor}`}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ delay: 0.4 + index * 0.08, duration: 1, ease: [0.4, 0, 0.2, 1] }}
          />
        </div>
      </div>
    </motion.div>
  );
}
