"use client";

import { useEffect, useState } from "react";

import { useProfile } from "@/lib/use-profile";

const ROLE_DATA = [
  { role: "Duelist", matches: 58, winrate: 62.1, kd: 0.94, adr: 147.3, color: "#ff4d67" },
  { role: "Controller", matches: 41, winrate: 56.1, kd: 0.87, adr: 127.0, color: "#5d7cff" },
  { role: "Initiator", matches: 4, winrate: 75.0, kd: 1.22, adr: 137.7, color: "#3FB950" },
  { role: "Sentinel", matches: 1, winrate: 100.0, kd: 0.94, adr: 130.5, color: "#F0A500" },
];

const AGENTS = [
  { name: "Jett", playtime: "27h 54m", winrate: 62.0, kd: 0.94, icon: "🗡️" },
  { name: "Omen", playtime: "15h 11m", winrate: 55.2, kd: 0.96, icon: "🌫️" },
  { name: "Sova", playtime: "8h 04m", winrate: 60.1, kd: 1.08, icon: "🏹" },
];

const MAPS = [
  { name: "Pearl", score: "15W - 4L", winrate: 78.9, kd: 1.01 },
  { name: "Abyss", score: "10W - 3L", winrate: 76.9, kd: 1.11 },
  { name: "Corrode", score: "8W - 4L", winrate: 66.7, kd: 0.85 },
];

export default function RolesPage() {
  const { profile } = useProfile();
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 120);
    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="fade-in">
      <div
        className="hero-banner"
        style={{
          height: 150,
          background:
            "radial-gradient(130% 110% at 0% 0%, rgba(255,70,85,0.3) 0%, rgba(123,47,190,0.15) 34%, transparent 66%), linear-gradient(180deg, rgba(6,10,27,0.3) 0%, rgba(6,10,27,1) 95%)",
        }}
      >
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
        <span className="hero-elyx-logo">ELYX</span>
        <div className="hero-content">
          <h1 style={{ fontSize: 26, fontWeight: 800, color: "var(--text-primary)" }}>Roles</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 12, marginTop: 4 }}>
            {profile?.nickname ?? "Player"} • {profile?.game_name ?? "Valorant"}
          </p>
        </div>
      </div>

      <section style={{ padding: "14px 16px 24px" }}>
        <div className="layout-grid-2">
          <div>
            <div className="section-hd" style={{ padding: "0 0 8px" }}>
              <span className="section-title">Role Breakdown</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {ROLE_DATA.map((row, idx) => (
                <article key={row.role} className="desktop-card" style={{ padding: 14 }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr 1fr", gap: 10, alignItems: "center" }}>
                    <div style={{ minWidth: 0 }}>
                      <p style={{ color: "var(--text-secondary)", fontSize: 12 }}>{row.matches} matches</p>
                      <h3 style={{ fontSize: 26, lineHeight: 1, marginTop: 5 }}>{row.role}</h3>
                    </div>
                    <div>
                      <p style={{ color: "var(--text-secondary)", fontSize: 11 }}>Win %</p>
                      <strong style={{ color: "#f4f6ff", fontSize: 18 }}>{row.winrate.toFixed(1)}%</strong>
                    </div>
                    <div>
                      <p style={{ color: "var(--text-secondary)", fontSize: 11 }}>K/D</p>
                      <strong style={{ color: "#f4f6ff", fontSize: 18 }}>{row.kd.toFixed(2)}</strong>
                    </div>
                    <div>
                      <p style={{ color: "var(--text-secondary)", fontSize: 11 }}>ADR</p>
                      <strong style={{ color: "#f4f6ff", fontSize: 18 }}>{row.adr.toFixed(1)}</strong>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, height: 4, borderRadius: 4, background: "rgba(122,139,220,0.2)", overflow: "hidden" }}>
                    <div
                      style={{
                        width: animate ? `${Math.min(100, row.winrate)}%` : "0%",
                        height: "100%",
                        background: `linear-gradient(90deg, ${row.color}, #ffd27a)`,
                        borderRadius: 4,
                        transition: `width 0.8s cubic-bezier(0.22,1,0.36,1) ${idx * 70}ms`,
                      }}
                    />
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="valo-side-col">
            <div className="section-hd" style={{ padding: "0 0 8px" }}>
              <span className="section-title">Best Agents</span>
            </div>
            <div className="desktop-card">
              {AGENTS.map((item) => (
                <div key={item.name} className="desktop-kv">
                  <span>{item.icon} {item.name} • {item.playtime}</span>
                  <strong>{item.winrate.toFixed(1)}% / {item.kd.toFixed(2)}</strong>
                </div>
              ))}
            </div>

            <div className="section-hd" style={{ padding: "8px 0" }}>
              <span className="section-title">Best Maps</span>
            </div>
            <div className="desktop-card">
              {MAPS.map((item) => (
                <div key={item.name} className="desktop-kv">
                  <span>{item.name} • {item.score}</span>
                  <strong>{item.winrate.toFixed(1)}% / {item.kd.toFixed(2)}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

