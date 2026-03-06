import { PageShell, SectionTitle } from "@/components/elyx/PageShell";
import { RoleBar } from "@/components/elyx/RoleBar";
import { roles, topAgents } from "@/lib/mock-data";
import { motion } from "framer-motion";
import { BarChart3, Users, Swords, Flame } from "lucide-react";

const agentColors: Record<string, string> = {
  Jett: "bg-neon-blue/15 text-neon-blue border-neon-blue/20",
  Neon: "bg-warning/15 text-warning border-warning/20",
  Brimstone: "bg-primary/15 text-primary border-primary/20",
  Omen: "bg-neon-purple/15 text-neon-purple border-neon-purple/20",
  Pearl: "bg-success/15 text-success border-success/20",
};

export default function StatsPage() {
  const totalMatches = roles.reduce((s, r) => s + r.matches, 0);

  return (
    <PageShell>
      <div className="px-4 md:px-6 pt-6 lg:pt-0 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold">Valorant</p>
          <div className="flex items-center gap-2 mt-0.5">
            <Flame size={20} className="text-primary" />
            <h1 className="font-display font-bold text-2xl tracking-tight">Power Stats</h1>
          </div>
        </div>

        {/* Rank distribution */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card-static rounded-2xl p-5 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/[0.03] via-transparent to-accent/[0.03]" />
          <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold mb-4 relative z-10">
            Распределение рангов
          </p>
          <div className="flex h-20 gap-1 items-end relative z-10">
            {[
              { pct: 3, color: "bg-muted-foreground/40" },
              { pct: 8, color: "bg-warning/50" },
              { pct: 12, color: "bg-muted-foreground/50" },
              { pct: 9, color: "bg-warning/60" },
              { pct: 6, color: "bg-neon-blue/50" },
              { pct: 5, color: "bg-neon-purple/60" },
              { pct: 3, color: "bg-success/50" },
              { pct: 2, color: "bg-primary/50" },
              { pct: 1, color: "bg-warning/70" },
            ].map(({ pct, color }, i) => (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                animate={{ height: `${Math.max(pct * 7, 5)}%` }}
                transition={{ delay: 0.1 + i * 0.06, duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                className={`flex-1 rounded-t-md ${color}`}
              />
            ))}
          </div>
          <div className="flex gap-1 mt-2 relative z-10">
            {["I", "B", "S", "G", "P", "D", "A", "Im", "R"].map((l) => (
              <span key={l} className="flex-1 text-center text-[9px] text-muted-foreground font-medium">{l}</span>
            ))}
          </div>
        </motion.div>

        {/* Roles */}
        <div>
          <SectionTitle
            icon={<Users size={16} className="text-primary" />}
            title="Роли"
            subtitle={`${totalMatches} матчей сыграно`}
          />
          <div className="space-y-2.5 mt-3">
            {roles.map((r, i) => (
              <RoleBar key={r.name} {...r} totalMatches={totalMatches} index={i} />
            ))}
          </div>
        </div>

        {/* Top agents */}
        <div>
          <SectionTitle
            icon={<Swords size={16} className="text-primary" />}
            title="Топ агенты"
          />
          <div className="space-y-2.5 mt-3">
            {topAgents.map((a, i) => {
              const colors = agentColors[a.name] || "bg-secondary text-foreground border-border/50";
              return (
                <motion.div
                  key={a.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.08, ease: [0.4, 0, 0.2, 1] }}
                  className="glass-card rounded-xl p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-11 h-11 rounded-xl flex items-center justify-center border ${colors} font-display font-bold text-xs`}>
                      {a.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-display font-bold text-sm">{a.name}</p>
                      <p className="text-[11px] text-muted-foreground">
                        {a.role} · {a.games} games · {a.playtime}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-display font-bold text-primary text-lg tabular-nums">
                      {a.kd.toFixed(2)}
                    </p>
                    <p className="text-[10px] text-muted-foreground font-medium">
                      Win <span className="text-success font-bold">{a.winRate}%</span>
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
