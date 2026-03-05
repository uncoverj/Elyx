"use client";

import { useEffect, useState } from "react";
import { useProfile } from "@/lib/use-profile";
import { SkeletonCard } from "@/components/skeleton";

const PROVIDER_CONFIG: Record<string, { label: string; icon: string; placeholder: string; hint: string }> = {
  riot: { label: "Riot Games", icon: "🎮", placeholder: "Имя#Тэг (например: Sygar#lovly)", hint: "Для Valorant и LoL. Формат: Nickname#TAG" },
  steam: { label: "Steam", icon: "🎯", placeholder: "Steam ID или ссылка на профиль", hint: "17-значный steam64 или vanity URL" },
  faceit: { label: "Faceit", icon: "🏆", placeholder: "Faceit никнейм (например: s1mple)", hint: "Для CS2. Ваш никнейм на faceit.com" },
  epic: { label: "Epic Games", icon: "🕹️", placeholder: "Epic Games ник", hint: "Для Fortnite" },
  blizzard: { label: "Blizzard", icon: "❄️", placeholder: "BattleTag (Имя#1234)", hint: "Для Overwatch 2. Формат: Name#1234" },
};

const GAME_PROVIDERS: Record<string, string[]> = {
  "Valorant": ["riot"],
  "CS2": ["faceit", "steam"],
  "League of Legends": ["riot"],
  "Dota 2": ["steam"],
  "Overwatch 2": ["blizzard"],
  "Fortnite": ["epic"],
  "Apex Legends": ["steam"],
};

const GAME_THEMES: Record<string, { gradient: string; accent: string }> = {
  "Valorant": { gradient: "linear-gradient(135deg, #fd4556 0%, #1f1225 100%)", accent: "#fd4556" },
  "CS2": { gradient: "linear-gradient(135deg, #de9b35 0%, #1a1a2e 100%)", accent: "#de9b35" },
  "League of Legends": { gradient: "linear-gradient(135deg, #c89b3c 0%, #091428 100%)", accent: "#c89b3c" },
  "Dota 2": { gradient: "linear-gradient(135deg, #e44d2e 0%, #1a1a2e 100%)", accent: "#e44d2e" },
  "Apex Legends": { gradient: "linear-gradient(135deg, #cd3333 0%, #1a1a2e 100%)", accent: "#cd3333" },
  "Overwatch 2": { gradient: "linear-gradient(135deg, #fa9c1e 0%, #1a1a2e 100%)", accent: "#fa9c1e" },
  "Fortnite": { gradient: "linear-gradient(135deg, #9d4dbb 0%, #1a1a2e 100%)", accent: "#9d4dbb" },
};
const DEFAULT_THEME = { gradient: "linear-gradient(135deg, #a78bfa 0%, #1a0a2e 100%)", accent: "#a78bfa" };

export default function AccountPage() {
  const { profile, games, loading, switchGame, linkAccount, refreshStats } = useProfile();
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [linking, setLinking] = useState<string | null>(null);
  const [linkSuccess, setLinkSuccess] = useState<string | null>(null);
  const [switching, setSwitching] = useState(false);
  const [tgUser, setTgUser] = useState<any>(null);

  useEffect(() => {
    const app = (window as any).Telegram?.WebApp;
    if (app?.initDataUnsafe?.user) setTgUser(app.initDataUnsafe.user);
  }, []);

  const handleLink = async (provider: string) => {
    if (!inputValue.trim()) return;
    setLinking(provider);
    try {
      await linkAccount(provider, inputValue.trim());
      setLinkSuccess(provider);
      setTimeout(() => setLinkSuccess(null), 3000);
      setEditingProvider(null);
      setInputValue("");
    } catch { }
    setLinking(null);
  };

  const handleSwitchGame = async (gameId: number) => {
    setSwitching(true);
    await switchGame(gameId);
    setSwitching(false);
  };

  const currentGameName = profile?.game_name || "";
  const relevantProviders = GAME_PROVIDERS[currentGameName] || ["riot", "steam", "faceit"];
  const theme = GAME_THEMES[currentGameName] || DEFAULT_THEME;

  if (loading) {
    return (
      <main className="fade-in" style={{ padding: 16 }}>
        <SkeletonCard lines={2} />
        <div style={{ marginTop: 12 }}><SkeletonCard lines={3} /></div>
        <div style={{ marginTop: 12 }}><SkeletonCard lines={2} /></div>
      </main>
    );
  }

  return (
    <main className="fade-in">
      {/* Hero */}
      <div className="hero-banner" style={{ background: theme.gradient, backgroundSize: "200% 200%", animation: "gradientShift 8s ease infinite" }}>
        <div className="hero-logo">{currentGameName?.substring(0, 4).toUpperCase() || "ELYX"}</div>
      </div>

      {/* Telegram Profile */}
      {tgUser && (
        <div className="section fade-in stagger-1" style={{ marginTop: 8 }}>
          <div className="card" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div className="avatar-ring" style={{ width: 44, height: 44 }}>
              <div className="avatar-placeholder" style={{ fontSize: 16 }}>{tgUser.first_name?.charAt(0) || "T"}</div>
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>{tgUser.first_name} {tgUser.last_name || ""}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>@{tgUser.username || "telegram"} • Telegram</div>
            </div>
            <div style={{ marginLeft: "auto", color: "var(--accent-green)", fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent-green)", boxShadow: "0 0 8px rgba(16,185,129,0.5)", display: "inline-block" }} />
              Онлайн
            </div>
          </div>
        </div>
      )}

      {/* Game Switcher Tabs */}
      <div className="section fade-in stagger-2">
        <h2 className="section-title slide-in-left">Игра</h2>
        <div className="game-tabs" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
          {games.map((g, i) => (
            <button
              key={g.id}
              className={`badge-pill fade-in ${profile?.game_id === g.id ? "active" : ""}`}
              style={{ animationDelay: `${0.1 + i * 0.05}s`, cursor: "pointer", opacity: switching ? 0.5 : 1 }}
              onClick={() => profile?.game_id !== g.id && handleSwitchGame(g.id)}
              disabled={switching}
            >
              {g.name}
            </button>
          ))}
        </div>
        {switching && (
          <div style={{ fontSize: 12, color: "var(--accent-purple)", textAlign: "center" }}>
            ⏳ Переключение игры и обновление статистики...
          </div>
        )}
      </div>

      {/* Account Linking */}
      <div className="section fade-in stagger-3">
        <h2 className="section-title slide-in-left">Привязка аккаунтов</h2>
        <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
          Привяжи аккаунт для {currentGameName}, чтобы получить реальную статистику
        </p>
        {relevantProviders.map((provider, i) => {
          const cfg = PROVIDER_CONFIG[provider] || { label: provider, icon: "🔗", placeholder: "Введи данные", hint: "" };
          return (
            <div key={provider} className="card fade-in" style={{
              marginBottom: 10, display: "flex", alignItems: "center", justifyContent: "space-between",
              animationDelay: `${0.2 + i * 0.08}s`,
              borderColor: linkSuccess === provider ? "rgba(16,185,129,0.3)" : undefined,
              boxShadow: linkSuccess === provider ? "0 0 16px rgba(16,185,129,0.15)" : undefined,
              transition: "border-color 0.5s ease, box-shadow 0.5s ease",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 20, filter: `drop-shadow(0 0 4px ${theme.accent}44)` }}>{cfg.icon}</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14 }}>{cfg.label}</div>
                  {linkSuccess === provider ? (
                    <div style={{ fontSize: 11, color: "var(--accent-green)" }}>✓ Подключено! Статистика обновляется...</div>
                  ) : (
                    <div style={{ fontSize: 10, color: "var(--text-muted)", maxWidth: 140 }}>{cfg.hint}</div>
                  )}
                </div>
              </div>

              {editingProvider === provider ? (
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <input
                    className="connect-input"
                    placeholder={cfg.placeholder}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    autoFocus
                    onKeyDown={(e) => { if (e.key === "Enter") handleLink(provider); if (e.key === "Escape") setEditingProvider(null); }}
                    style={{ width: 180, fontSize: 12 }}
                  />
                  <button className="btn btn-connect" onClick={() => handleLink(provider)} disabled={linking === provider}>
                    {linking === provider ? "..." : "→"}
                  </button>
                </div>
              ) : (
                <button className="btn btn-connect" onClick={() => { setEditingProvider(provider); setInputValue(""); }}
                  style={{ background: "var(--accent-blue)", fontSize: 12 }}>
                  Привязать
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Swap to Games */}
      <div className="section fade-in stagger-5">
        <h2 className="section-title slide-in-left">Swap to</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {games.map((g, i) => (
            <button
              key={g.id}
              onClick={() => profile?.game_id !== g.id && handleSwitchGame(g.id)}
              disabled={switching}
              className="fade-in"
              style={{
                animationDelay: `${0.1 + i * 0.05}s`,
                padding: "8px 12px",
                borderRadius: "12px",
                border: "1px solid var(--border)",
                background: profile?.game_id === g.id ? "var(--accent-orange)" : "var(--bg-card)",
                color: "var(--text-primary)",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s ease",
                opacity: switching ? 0.5 : 1,
              }}
            >
              {g.name === "Valorant" && "🎯 VALORANT"}
              {g.name === "CS2" && "🔫 CS2★"}
              {g.name === "League of Legends" && "⚔️ LoL"}
              {g.name === "Dota 2" && "🛡️ DOTA2"}
              {g.name === "Fortnite" && "🏗️ FORTNITE"}
              {g.name === "Apex Legends" && "🏹 APEX"}
              {g.name === "Overwatch 2" && "🌟 OW2"}
            </button>
          ))}
        </div>
      </div>

      {/* Refresh */}
      <div className="section fade-in stagger-6" style={{ textAlign: "center", paddingBottom: 24 }}>
        <button className="btn btn-connect" onClick={async () => { await refreshStats(); }}
          style={{ background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}99)` }}>
          🔄 Обновить статистику
        </button>
      </div>
    </main>
  );
}
