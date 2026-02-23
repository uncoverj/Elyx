"use client";

import { useEffect, useState } from "react";

import ProfileCard from "@/components/profile-card";
import WebAppInit from "@/components/webapp-init";
import { backendFetch } from "@/lib/api";

type Profile = {
  user_id: number;
  nickname: string;
  age: number;
  gender: string;
  game_name: string;
  roles: string[];
  tags: string[];
  bio: string;
  trust_up: number;
  trust_down: number;
  stats?: { kd?: number | null; winrate?: number | null; rank_name?: string | null } | null;
};

export default function HomePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const result = await backendFetch("/profiles/me");
        setProfile(result);
      } catch (e: any) {
        setError("Профиль пока не заполнен. Сделай это в боте через /start.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  return (
    <main className="grid">
      <WebAppInit />
      <section className="card">
        <h1>Elyx Mini App</h1>
        <p>Профиль, статистика, настройки и премиум внутри Telegram.</p>
      </section>

      {loading && <div className="card">Загрузка...</div>}
      {error && <div className="card">{error}</div>}
      {profile && <ProfileCard profile={profile} />}
    </main>
  );
}
