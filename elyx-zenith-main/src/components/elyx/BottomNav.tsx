import { useLocation, useNavigate } from "react-router-dom";
import { Crosshair, BarChart3, Trophy, Clock, Settings } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
  { path: "/", icon: Crosshair, label: "Power" },
  { path: "/stats", icon: BarChart3, label: "Stats" },
  { path: "/leaderboard", icon: Trophy, label: "Leader" },
  { path: "/matches", icon: Clock, label: "Matches" },
  { path: "/settings", icon: Settings, label: "Settings" },
];

export function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 lg:hidden"
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Blur backdrop */}
      <div className="absolute inset-0 glass" />
      
      <div className="relative flex items-center justify-around px-2 pt-2.5 safe-bottom">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="tap-target flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl transition-all duration-200 relative focus-ring"
              aria-label={item.label}
              aria-current={isActive ? "page" : undefined}
            >
              {isActive && (
                <motion.div
                  layoutId="nav-bg"
                  className="absolute inset-0 rounded-xl bg-primary/10"
                  transition={{ type: "spring", stiffness: 400, damping: 28 }}
                />
              )}
              <item.icon
                size={20}
                strokeWidth={isActive ? 2.5 : 1.8}
                className={`relative z-10 transition-colors duration-200 ${isActive ? "text-primary" : "text-muted-foreground"}`}
              />
              <span className={`text-[10px] font-semibold relative z-10 transition-colors duration-200 ${isActive ? "text-primary" : "text-muted-foreground"}`}>
                {item.label}
              </span>
              {isActive && (
                <motion.div
                  layoutId="nav-dot"
                  className="absolute -bottom-0.5 w-1 h-1 rounded-full bg-primary"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
