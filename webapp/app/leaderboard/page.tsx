"use client";

import { useEffect, useState } from "react";

import { leaderboardApi } from "@/lib/api";
import { useProfile } from "@/lib/use-profile";

type Entry = {
  position: number;
  user_id: number;
  nickname: string;
  rank_name: string | null;
  unified_score: number;
  is_premium: boolean;
};

const CHART_DATA = [
  { rank: "Iron", pct: 14, color: "#6B7280" },
  { rank: "Bronze", pct: 20, color: "#A16207" },
  { rank: "Silver", pct: 26, color: "#9CA3AF" },
  { rank: "Gold", pct: 18, color: "#F0A500" },
  { rank: "Plat", pct: 10, color: "#4A9EFF" },
  { rank: "Diamond", pct: 7, color: "#818CF8" },
  { rank: "Asc", pct: 3, color: "#3FB950" },
  { rank: "Imm", pct: 1.5, color: "#EF4444" },
  { rank: "Rad", pct: 0.5, color: "#F9A825" },
];

const MOCK: Entry[] = [
  { position: 1, user_id: 101, nickname: "QOR twitch Smoke", rank_name: "Radiant", unified_score: 1003, is_premium: true },
  { position: 2, user_id: 102, nickname: "EP kozzy", rank_name: "Radiant", unified_score: 976, is_premium: false },
  { position: 3, user_id: 103, nickname: "TI Satoru", rank_name: "Radiant", unified_score: 965, is_premium: false },
  { position: 4, user_id: 104, nickname: "KRU dante", rank_name: "Radiant", unified_score: 940, is_premium: false },
  { position: 5, user_id: 105, nickname: "MercureFPS", rank_name: "Radiant", unified_score: 931, is_premium: false },
  { position: 6, user_id: 106, nickname: "GL hAwksinho", rank_name: "Radiant", unified_score: 905, is_premium: false },
  { position: 7, user_id: 107, nickname: "MISA BadreX", rank_name: "Radiant", unified_score: 900, is_premium: false },
  { position: 8, user_id: 108, nickname: "lorem", rank_name: "Radiant", unified_score: 856, is_premium: false },
];

const MEDALS: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export default function LeaderboardPage() {
  const { profile } = useProfile();
  const [entries, setEntries] = useState<Entry[]>(MOCK);
  const [animateBars, setAnimateBars] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimateBars(true), 120);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!profile?.game_id) return;
    leaderboardApi
      .get(profile.game_id)
      .then((data: any) => {
        if (Array.isArray(data?.entries) && data.entries.length > 0) {
          setEntries(data.entries as Entry[]);
        }
      })
      .catch(() => {
        /* keep mock */
      });
  }, [profile?.game_id]);

  const maxPct = Math.max(...CHART_DATA.map((d) => d.pct));

  return (
    <main className="fade-in">
      <div
        className="hero-banner"
        style={{
          height: 150,
          background:
            "radial-gradient(120% 110% at 0% 0%, rgba(255,70,85,0.32) 0%, rgba(255,70,85,0.1) 30%, transparent 64%), linear-gradient(180deg, rgba(6,10,27,0.2) 0%, rgba(6,10,27,1) 95%)",
        }}
      >
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
        <span className="hero-elyx-logo">ELYX</span>
        <div className="hero-content">
          <h1 style={{ fontSize: 26, fontWeight: 800, color: "var(--text-primary)" }}>Leaderboard</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 12, marginTop: 4 }}>
            {profile?.game_name ?? "Valorant"} • {entries.length} players
          </p>
        </div>
      </div>

      <section style={{ padding: "14px 16px 24px" }}>
        <div className="layout-grid-2">
          <div>
            <div className="section-hd" style={{ padding: "0 0 8px" }}>
              <span className="section-title">Rank Distribution</span>
            </div>
            <div className="rank-chart">
              {CHART_DATA.map((bar, i) => (
                <div key={bar.rank} className="rank-chart-bar-wrap">
                  <div
                    className="rank-chart-bar"
                    style={{
                      backgroundColor: bar.color,
                      opacity: 0.82,
                      height: animateBars ? `${(bar.pct / maxPct) * 52}px` : "2px",
                      transition: `height 0.65s cubic-bezier(0.22,1,0.36,1) ${i * 40}ms`,
                    }}
                  />
                  <span className="rank-chart-label">{bar.rank}</span>
                </div>
              ))}
            </div>

            <div className="filter-pills" style={{ marginTop: 12, paddingLeft: 0 }}>
              {["Game Rank", "Trust", "Rating"].map((item, idx) => (
                <button key={item} className={`filter-pill${idx === 0 ? " active" : ""}`}>{item}</button>
              ))}
            </div>
          </div>

          <div className="desktop-card">
            <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8 }}>Top 3 Snapshot</p>
            {entries.slice(0, 3).map((item) => (
              <div key={item.user_id} className="desktop-kv">
                <span>{MEDALS[item.position]} {item.nickname}</span>
                <strong>{item.unified_score.toLocaleString()}</strong>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 14 }}>
          {entries.map((item) => {
            const top3 = item.position <= 3;
            return (
              <div key={item.user_id} className={`lb-row${top3 ? " top3" : ""}`}>
                <div className="lb-pos">
                  {top3 ? <span style={{ fontSize: 20 }}>{MEDALS[item.position]}</span> : <span className="lb-pos-num">{item.position}</span>}
                </div>

                <div
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: "50%",
                    flexShrink: 0,
                    background: top3 ? "linear-gradient(135deg, #F0A500, #FF6B00)" : "var(--bg-card-elevated)",
                    border: "1px solid var(--border-default)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: top3 ? "#000" : "var(--text-secondary)",
                    fontSize: 14,
                    fontWeight: 800,
                  }}
                >
                  {item.nickname.slice(0, 1).toUpperCase()}
                </div>

                <div className="lb-name">
                  <p>{item.nickname}{item.is_premium ? " ⭐" : ""}</p>
                  <span>{item.rank_name ?? "Unrated"}</span>
                </div>

                <div className="lb-score">
                  <p className="lb-score-val">{item.unified_score.toLocaleString()}</p>
                  <p className="lb-score-sub">score</p>
                </div>

                <div className={`lb-tier ${top3 ? "top" : "mid"}`}>{top3 ? "TOP" : "—"}</div>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}

