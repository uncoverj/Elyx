import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string | number;
  percentile: number;
  delay?: number;
  size?: "sm" | "md";
}

export function StatCard({ label, value, percentile, delay = 0, size = "md" }: StatCardProps) {
  const isTop = percentile >= 70;
  const isBottom = percentile <= 30;
  const barColor = isTop ? "bg-success" : isBottom ? "bg-destructive" : "bg-warning";
  const textColor = isTop ? "text-success" : isBottom ? "text-destructive" : "text-warning";
  const percentileLabel = isTop ? `Top ${100 - percentile}%` : isBottom ? `Bottom ${percentile}%` : `${percentile}%`;
  const glowClass = isTop ? "glow-success" : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      className={`glass-card rounded-xl ${size === "sm" ? "p-3" : "p-4"} group`}
    >
      <p className="text-[11px] text-muted-foreground font-medium uppercase tracking-wider mb-1.5">{label}</p>
      <p className={`${size === "sm" ? "text-xl" : "text-2xl"} font-display font-bold tracking-tight`}>{value}</p>
      <p className={`text-[11px] mt-1 font-semibold ${textColor}`}>
        {percentileLabel}
      </p>
      <div className="stat-bar mt-2.5">
        <motion.div
          className={`stat-bar-fill ${barColor}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentile}%` }}
          transition={{ delay: delay + 0.3, duration: 1, ease: [0.4, 0, 0.2, 1] }}
        />
      </div>
    </motion.div>
  );
}
