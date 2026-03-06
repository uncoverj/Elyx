import { PageShell, SectionTitle } from "@/components/elyx/PageShell";
import { MatchCard } from "@/components/elyx/MatchCard";
import { matches } from "@/lib/mock-data";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Search, SlidersHorizontal } from "lucide-react";

const filters = ["Все", "Побед", "Поражений", "Competitive", "Spike Rush"];

export default function MatchesPage() {
  const [activeFilter, setActiveFilter] = useState("Все");

  const filtered = matches.filter((m) => {
    if (activeFilter === "Все") return true;
    if (activeFilter === "Побед") return m.won;
    if (activeFilter === "Поражений") return !m.won;
    return m.mode === activeFilter;
  });

  const grouped = filtered.reduce<Record<string, typeof matches>>((acc, m) => {
    const key = m.dateLabel;
    if (!acc[key]) acc[key] = [];
    acc[key].push(m);
    return acc;
  }, {});

  return (
    <PageShell>
      <div className="px-4 md:px-6 pt-6 lg:pt-0 max-w-5xl mx-auto space-y-5">
        <SectionTitle
          icon={<Clock size={20} className="text-primary" />}
          title="История матчей"
          subtitle={`${matches.length} матчей`}
        />

        {/* Filters */}
        <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all duration-200 ${
                activeFilter === f ? "pill-active" : "pill-inactive"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Match groups */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeFilter}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="space-y-5"
          >
            {Object.entries(grouped).map(([date, dateMatches]) => {
              const wins = dateMatches.filter(m => m.won).length;
              const losses = dateMatches.length - wins;
              const avgKd = (dateMatches.reduce((s, m) => s + m.kd, 0) / dateMatches.length).toFixed(2);
              const avgDmg = Math.round(dateMatches.reduce((s, m) => s + m.damagePerRound, 0) / dateMatches.length);

              return (
                <div key={date} className="space-y-2">
                  {/* Date header */}
                  <div className="glass-card-static rounded-xl px-4 py-2.5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <h3 className="text-sm font-display font-bold">{date}</h3>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${wins > losses ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"}`}>
                        {dateMatches.length} матчей
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                      <span>К/Д <span className="text-foreground font-mono font-bold">{avgKd}</span></span>
                      <span>У/Р <span className="text-foreground font-mono font-bold">{avgDmg}</span></span>
                      <span>
                        <span className="text-success font-bold">{wins}W</span>{" "}
                        <span className="text-destructive font-bold">{losses}L</span>
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {dateMatches.map((m, i) => (
                      <MatchCard key={m.id} match={m} index={i} />
                    ))}
                  </div>
                </div>
              );
            })}
          </motion.div>
        </AnimatePresence>

        {filtered.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <div className="w-16 h-16 rounded-2xl bg-secondary mx-auto flex items-center justify-center mb-4">
              <Search size={24} className="text-muted-foreground" />
            </div>
            <p className="text-muted-foreground font-medium">Нет матчей для выбранного фильтра</p>
            <button
              onClick={() => setActiveFilter("Все")}
              className="mt-3 text-xs text-primary font-bold hover:underline"
            >
              Показать все матчи
            </button>
          </motion.div>
        )}
      </div>
    </PageShell>
  );
}
