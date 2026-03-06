import { PageShell, SectionTitle } from "@/components/elyx/PageShell";
import { motion } from "framer-motion";
import { Settings, CheckCircle2, XCircle, ArrowRight } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "@/components/ui/sonner";
import { useElyx } from "@/context/ElyxContext";

const PROVIDER_LABELS: Record<string, string> = {
  riot: "Riot Games",
  steam: "Steam",
  faceit: "Faceit",
  blizzard: "Battle.net",
  epic: "Epic Games",
};

const platformIcons: Record<string, string> = {
  riot: "🎯",
  steam: "🎮",
  faceit: "⚡",
  blizzard: "❄️",
  epic: "🎪",
};

const placeholders: Record<string, string> = {
  riot: "Nickname#TAG",
  steam: "Steam ID / vanity",
  faceit: "Faceit nickname",
  blizzard: "BattleTag",
  epic: "Epic username",
};

export default function SettingsPage() {
  const { profile, accounts, games, linkAccount, switchGame } = useElyx();
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [savingProvider, setSavingProvider] = useState<string | null>(null);
  const [switchingGame, setSwitchingGame] = useState<number | null>(null);

  const orderedAccounts = useMemo(() => {
    const rank = { riot: 1, steam: 2, faceit: 3, blizzard: 4, epic: 5 } as Record<string, number>;
    return [...accounts].sort((a, b) => (rank[a.provider] || 99) - (rank[b.provider] || 99));
  }, [accounts]);

  const handleConnect = async (provider: string) => {
    const value = (inputs[provider] || "").trim();
    if (!value) {
      toast.error("Введите логин или ID");
      return;
    }

    setSavingProvider(provider);
    const result = await linkAccount(provider, value);
    setSavingProvider(null);

    if (!result.ok) {
      toast.error(result.error || "Ошибка подключения");
      return;
    }

    setInputs((prev) => ({ ...prev, [provider]: "" }));
    toast.success(`${PROVIDER_LABELS[provider] || provider} connected`);
  };

  const handleSwitchGame = async (gameId: number) => {
    setSwitchingGame(gameId);
    const result = await switchGame(gameId);
    setSwitchingGame(null);
    if (!result.ok) {
      toast.error(result.error || "Не удалось переключить игру");
      return;
    }
    toast.success("Игра обновлена");
  };

  return (
    <PageShell>
      <div className="px-4 md:px-6 pt-6 lg:pt-0 max-w-5xl mx-auto space-y-8">
        <SectionTitle icon={<Settings size={20} className="text-primary" />} title="Настройки" />

        <div className="space-y-3">
          <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold">
            Привязанные аккаунты
          </p>

          {orderedAccounts.length === 0 ? (
            <div className="glass-card rounded-2xl p-5">
              <p className="text-sm font-medium">Нет данных для подключения аккаунтов</p>
              <p className="text-xs text-muted-foreground mt-1">
                Открой сайт из Telegram Mini App или задайте `VITE_SERVICE_TOKEN` и `VITE_TELEGRAM_ID` для dev-режима.
              </p>
            </div>
          ) : null}

          {orderedAccounts.map((acc, i) => {
            const provider = acc.provider;
            const label = PROVIDER_LABELS[provider] || provider;
            const isSaving = savingProvider === provider;
            const isConnected = acc.connected;

            return (
              <motion.div
                key={provider}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06, ease: [0.4, 0, 0.2, 1] }}
                className="glass-card rounded-2xl p-5 relative overflow-hidden"
              >
                {isConnected ? (
                  <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-success/60 via-success/20 to-transparent" />
                ) : null}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{platformIcons[provider] || "🎮"}</span>
                    <div>
                      <p className="font-display font-bold text-sm">{label}</p>
                      <p className="text-[11px] text-muted-foreground">
                        {isConnected ? acc.account_ref : `Connect ${label}`}
                      </p>
                    </div>
                  </div>

                  {isConnected ? (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-success/10 border border-success/20">
                      <CheckCircle2 size={13} className="text-success" />
                      <span className="text-[11px] text-success font-bold">Connected</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                      <XCircle size={13} />
                      <span>disconnected</span>
                    </div>
                  )}
                </div>

                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="flex gap-2 mt-4"
                >
                  <input
                    type="text"
                    placeholder={placeholders[provider] || "Введите логин..."}
                    value={inputs[provider] || ""}
                    onChange={(e) => setInputs((prev) => ({ ...prev, [provider]: e.target.value }))}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-input border border-border text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
                    aria-label={`${label} логин`}
                  />
                  <button
                    onClick={() => handleConnect(provider)}
                    disabled={isSaving}
                    className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground text-xs font-bold hover:bg-primary-glow transition-all duration-200 flex items-center gap-1.5 glow-red disabled:opacity-60"
                  >
                    {isSaving ? "..." : "Connect"}
                    <ArrowRight size={13} />
                  </button>
                </motion.div>
              </motion.div>
            );
          })}
        </div>

        <div>
          <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground font-bold text-center mb-4">
            Переключить игру
          </p>
          <div className="flex justify-center gap-2.5 flex-wrap">
            {games.map((g, i) => (
              <motion.button
                key={g.id}
                initial={{ opacity: 0, scale: 0.92 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + i * 0.05 }}
                onClick={() => handleSwitchGame(g.id)}
                disabled={switchingGame === g.id}
                className={`px-5 py-3 rounded-xl text-xs font-bold transition-all duration-200 ${
                  profile?.game_id === g.id ? "pill-active" : "glass-card text-muted-foreground"
                } ${switchingGame === g.id ? "opacity-60" : ""}`}
              >
                {g.name}
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
