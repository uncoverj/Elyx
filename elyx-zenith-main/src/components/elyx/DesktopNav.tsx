import { useLocation, useNavigate } from "react-router-dom";
import { Crosshair, BarChart3, Trophy, Clock, Settings } from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { path: "/", icon: Crosshair, label: "Power" },
  { path: "/stats", icon: BarChart3, label: "Stats" },
  { path: "/leaderboard", icon: Trophy, label: "Leaderboard" },
  { path: "/matches", icon: Clock, label: "Matches" },
  { path: "/settings", icon: Settings, label: "Settings" },
];

export function DesktopNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="hidden lg:block fixed top-0 left-0 right-0 z-50" role="navigation" aria-label="Desktop navigation">
      <div className="absolute inset-0 glass" />
      <div className="relative container flex items-center justify-between h-16">
        <button onClick={() => navigate("/")} className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20 group-hover:border-primary/40 transition-colors">
            <Crosshair size={16} className="text-primary" />
          </div>
          <span className="font-display text-xl font-bold gradient-text tracking-wider">ELYX</span>
        </button>
        <div className="flex items-center gap-1 bg-secondary/50 rounded-xl p-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring ${
                  isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="desktop-nav-bg"
                    className="absolute inset-0 rounded-lg bg-primary/10 border border-primary/20"
                    transition={{ type: "spring", stiffness: 400, damping: 28 }}
                  />
                )}
                <item.icon size={16} className="relative z-10" />
                <span className="relative z-10">{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
