"use client";

import { useMemo, useState } from "react";
import { useProfile } from "@/lib/use-profile";

type AccountPreset = {
  provider: string;
  name: string;
  placeholder: string;
  hint: string;
};

const ACCOUNT_PRESETS: AccountPreset[] = [
  { provider: "riot", name: "Riot Games", placeholder: "Nickname#TAG", hint: "Valorant и LoL" },
  { provider: "steam", name: "Steam", placeholder: "Steam ID / vanity URL", hint: "CS2" },
  { provider: "faceit", name: "Faceit", placeholder: "Faceit nickname", hint: "CS2 Faceit" },
  { provider: "epic", name: "Epic Games", placeholder: "Epic nickname", hint: "Fortnite" },
];

const GAME_ORDER = ["Valorant", "CS2", "League of Legends", "Dota 2", "Fortnite"];

function gameShort(name: string) {
  if (name === "League of Legends") return "LoL";
  return name;
}

export default function SettingsPage() {
  const { profile, accounts, games, linkAccount, switchGame } = useProfile();
  const [editing, setEditing] = useState<string | null>(null);
  const [inputVal, setInputVal] = useState("");
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const linkedMap = useMemo(
    () =>
      accounts.reduce<Record<string, string>>((acc, item) => {
        if (item.connected && item.account_ref) acc[item.provider] = item.account_ref;
        return acc;
      }, {}),
    [accounts]
  );

  const orderedGames = useMemo(() => {
    return [...games].sort((a, b) => {
      const ai = GAME_ORDER.indexOf(a.name);
      const bi = GAME_ORDER.indexOf(b.name);
      if (ai === -1 && bi === -1) return a.name.localeCompare(b.name);
      if (ai === -1) return 1;
      if (bi === -1) return -1;
      return ai - bi;
    });
  }, [games]);

  const handleStartEdit = (provider: string) => {
    setError(null);
    setEditing(provider);
    setInputVal(linkedMap[provider] ?? "");
  };

  const handleLink = async (provider: string) => {
    const value = inputVal.trim();
    if (!value) {
      setError("Введите ID или ник.");
      return;
    }
    setSaving(provider);
    setError(null);
    try {
      await linkAccount(provider, value);
      setEditing(null);
      setInputVal("");
    } catch (e: any) {
      setError(e?.message || "Не удалось сохранить аккаунт.");
    } finally {
      setSaving(null);
    }
  };

  return (
    <main className="fade-in">
      <div
        className="hero-banner"
        style={{
          height: 132,
          background:
            "radial-gradient(120% 120% at 0% 0%, rgba(255,70,85,0.35) 0%, rgba(255,70,85,0.12) 25%, transparent 60%), linear-gradient(180deg, rgba(6,10,27,0.2) 0%, rgba(6,10,27,1) 95%)",
        }}
      >
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, transparent 40%, var(--bg-surface) 100%)" }} />
        <span className="hero-elyx-logo">ELYX</span>
        <div className="hero-content">
          <h1 style={{ fontSize: 22, fontWeight: 900, color: "var(--text-primary)" }}>Настройки</h1>
        </div>
      </div>

      <section style={{ margin: "0 0 18px", padding: "0 12px" }}>
        <div className="card" style={{ padding: 0, borderRadius: 22, overflow: "hidden", background: "#0d1334", borderColor: "#1a2152" }}>
          {ACCOUNT_PRESETS.map((acc, idx) => {
            const isLinked = Boolean(linkedMap[acc.provider]);
            const isEditing = editing === acc.provider;
            return (
              <div key={acc.provider} style={{ borderTop: idx === 0 ? "none" : "1px solid rgba(109,123,192,0.18)", padding: "14px 14px 12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 20, lineHeight: 1.2, fontWeight: 700 }}>{acc.name}</p>
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                      {isLinked ? linkedMap[acc.provider] : acc.hint}
                    </p>
                  </div>
                  {!isEditing && (
                    <button
                      onClick={() => handleStartEdit(acc.provider)}
                      style={{
                        border: "none",
                        background: "transparent",
                        color: isLinked ? "#a8b4ff" : "var(--text-secondary)",
                        fontSize: 16,
                        cursor: "pointer",
                        padding: 0,
                      }}
                    >
                      {isLinked ? "connect" : "disconnected"}
                    </button>
                  )}
                </div>

                {isEditing && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8, marginTop: 10 }}>
                    <input
                      value={inputVal}
                      onChange={(e) => setInputVal(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleLink(acc.provider)}
                      placeholder={acc.placeholder}
                      autoFocus
                      style={{
                        width: "100%",
                        background: "#181f4f",
                        border: "1px solid #242d6a",
                        borderRadius: 10,
                        color: "var(--text-primary)",
                        height: 40,
                        padding: "0 12px",
                        outline: "none",
                      }}
                    />
                    <button
                      onClick={() => handleLink(acc.provider)}
                      disabled={saving === acc.provider}
                      style={{
                        border: "none",
                        borderRadius: 10,
                        background: "linear-gradient(135deg, #f04367 0%, #ff6b7f 100%)",
                        color: "#fff",
                        fontWeight: 700,
                        height: 40,
                        padding: "0 16px",
                        cursor: "pointer",
                        minWidth: 95,
                      }}
                    >
                      {saving === acc.provider ? "..." : "Connect"}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {error && (
          <div style={{ marginTop: 10, fontSize: 13, color: "#ff9daf", paddingLeft: 4 }}>{error}</div>
        )}
      </section>

      <section style={{ padding: "0 12px 24px" }}>
        <div className="card" style={{ padding: "14px 14px 12px", borderRadius: 22, background: "#0d1334", borderColor: "#1a2152" }}>
          <p style={{ textAlign: "center", color: "var(--text-primary)", marginBottom: 12, fontSize: 22 }}>Swap to</p>
          <div style={{ display: "flex", gap: 8, overflowX: "auto", scrollbarWidth: "none", paddingBottom: 2 }}>
            {orderedGames.map((g) => (
              <button
                key={g.id}
                onClick={() => switchGame(g.id)}
                className={`game-pill${profile?.game_id === g.id ? " active" : ""}`}
                style={{
                  minWidth: 74,
                  padding: "9px 12px",
                  borderRadius: 12,
                  fontSize: 12,
                  background: profile?.game_id === g.id ? "linear-gradient(135deg, #f9a825 0%, #ea8e17 100%)" : "#1a214f",
                  borderColor: profile?.game_id === g.id ? "transparent" : "#2b3577",
                  color: profile?.game_id === g.id ? "#111" : "#d6dcff",
                  boxShadow: "none",
                }}
              >
                {gameShort(g.name)}
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
