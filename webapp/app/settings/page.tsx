"use client";

import { useState } from "react";
import { useProfile } from "@/lib/use-profile";

const ACCOUNT_PRESETS = [
  {
    provider: "riot",
    name: "Riot Games",
    icon: "🎮",
    iconBg: "rgba(255,70,85,0.15)",
    iconBorder: "rgba(255,70,85,0.25)",
    placeholder: "Nickname#TAG",
    desc: "Valorant и LoL · Формат: Nickname#TAG",
  },
  {
    provider: "steam",
    name: "Steam",
    icon: "🎯",
    iconBg: "rgba(74,158,255,0.15)",
    iconBorder: "rgba(74,158,255,0.25)",
    placeholder: "Steam ID / vanity URL",
    desc: "CS2 · Steam64 ID или vanity URL",
  },
  {
    provider: "faceit",
    name: "Faceit",
    icon: "🏆",
    iconBg: "rgba(240,165,0,0.15)",
    iconBorder: "rgba(240,165,0,0.25)",
    placeholder: "Ваш никнейм на faceit.com",
    desc: "CS2 · Ваш никнейм на faceit.com",
  },
  {
    provider: "epic",
    name: "Epic Games",
    icon: "🌀",
    iconBg: "rgba(123,47,190,0.15)",
    iconBorder: "rgba(123,47,190,0.25)",
    placeholder: "Epic Games никнейм",
    desc: "Fortnite · Epic Games никнейм",
  },
];

const GAMES = [
  { id: 1, name: "VALORANT" },
  { id: 2, name: "CS2" },
  { id: 4, name: "LoL" },
  { id: 3, name: "Dota 2" },
  { id: 7, name: "Fortnite" },
];

export default function SettingsPage() {
  const { profile, accounts, linkAccount, switchGame } = useProfile();
  const [editing, setEditing] = useState<string | null>(null);
  const [inputVal, setInputVal] = useState("");
  const [saving, setSaving] = useState<string | null>(null);

  const handleLink = async (provider: string) => {
    if (!inputVal.trim()) return;
    setSaving(provider);
    try {
      await linkAccount(provider, inputVal.trim());
    } catch { }
    setEditing(null);
    setInputVal("");
    setSaving(null);
  };

  const linkedMap = accounts.reduce<Record<string, string>>((acc, item) => {
    if (item.connected && item.account_ref) {
      acc[item.provider] = item.account_ref;
    }
    return acc;
  }, {});

  return (
    <main className="fade-in">
      {/* Hero */}
      <div className="hero-banner" style={{ height: 120, background: "linear-gradient(180deg, rgba(123,47,190,0.15) 0%, transparent 100%)" }}>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
        <span className="hero-elyx-logo">ELYX</span>
        <div className="hero-content">
          <h1 style={{ fontSize: 22, fontWeight: 900, color: "var(--text-primary)" }}>⚙️ Настройки</h1>
        </div>
      </div>

      {/* Account Links */}
      <div className="section-hd" style={{ marginTop: 8 }}>
        <span className="section-title">Привязанные аккаунты</span>
      </div>
      <div className="space-y-3" style={{ padding: "0 16px" }}>
        {ACCOUNT_PRESETS.map(acc => {
          const isLinked = Boolean(linkedMap[acc.provider]);
          const isEditing = editing === acc.provider;
          return (
            <div key={acc.provider} style={{ display: "flex", flexDirection: "column", gap: isEditing ? 10 : 0 }}>
              <div className="account-card">
                {/* Icon */}
                <div className="account-icon" style={{ background: acc.iconBg, border: `1px solid ${acc.iconBorder}` }}>
                  {acc.icon}
                </div>

                {/* Info */}
                <div className="account-info">
                  <p className="account-name">{acc.name}</p>
                  <p className="account-ref">
                    {isLinked ? linkedMap[acc.provider] : acc.desc}
                  </p>
                </div>

                {/* Button */}
                {isLinked ? (
                  <button className="btn-linked" onClick={() => { setEditing(acc.provider); setInputVal(""); }}>
                    Привязан ✓
                  </button>
                ) : (
                  <button className="btn-link" onClick={() => { setEditing(acc.provider); setInputVal(""); }}>
                    Привязать
                  </button>
                )}
              </div>

              {/* Inline input for editing */}
              {isEditing && (
                <div style={{ display: "flex", gap: 8, padding: "0 2px" }}>
                  <input
                    value={inputVal}
                    onChange={e => setInputVal(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && handleLink(acc.provider)}
                    placeholder={acc.placeholder}
                    autoFocus
                    style={{
                      flex: 1,
                      background: "var(--bg-card)",
                      border: "1px solid var(--border-default)",
                      borderRadius: 12,
                      padding: "10px 14px",
                      color: "var(--text-primary)",
                      fontSize: 13,
                      outline: "none",
                    }}
                  />
                  <button
                    onClick={() => handleLink(acc.provider)}
                    disabled={saving === acc.provider}
                    style={{
                      padding: "10px 16px",
                      borderRadius: 12,
                      background: "var(--gradient-accent)",
                      color: "#fff",
                      fontWeight: 700,
                      fontSize: 13,
                      border: "none",
                      cursor: "pointer",
                      flexShrink: 0,
                    }}
                  >
                    {saving === acc.provider ? "..." : "OK"}
                  </button>
                  <button
                    onClick={() => setEditing(null)}
                    style={{
                      padding: "10px 14px",
                      borderRadius: 12,
                      background: "var(--bg-card)",
                      color: "var(--text-secondary)",
                      fontWeight: 600,
                      fontSize: 13,
                      border: "1px solid var(--border-default)",
                      cursor: "pointer",
                      flexShrink: 0,
                    }}
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Game switcher */}
      <div className="section-hd" style={{ marginTop: 24 }}>
        <span className="section-title">Текущая игра</span>
      </div>
      <div className="game-pills" style={{ paddingBottom: 24 }}>
        {GAMES.map(g => (
          <button
            key={g.id}
            className={`game-pill${profile?.game_id === g.id ? " active" : ""}`}
            onClick={() => switchGame(g.id)}
          >
            {g.name}
          </button>
        ))}
      </div>
    </main>
  );
}
