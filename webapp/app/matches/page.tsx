"use client";

import { useEffect, useState } from "react";

import { backendFetch } from "@/lib/api";

type Match = {
  match_id: number;
  user_id: number;
  nickname: string;
  username?: string | null;
  game_name: string;
};

export default function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const rows = await backendFetch("/matches");
        setMatches(rows);
      } catch (e: any) {
        setError(e.message || "Failed to load matches");
      }
    };
    run();
  }, []);

  return (
    <main className="card grid">
      <h1>Мэтчи</h1>
      {error && <p>{error}</p>}
      {!error && matches.length === 0 && <p>Пока нет мэтчей</p>}
      {matches.map((item) => (
        <div key={item.match_id} className="card">
          <strong>{item.nickname}</strong>
          <p>{item.game_name}</p>
          <p>{item.username ? `@${item.username}` : "Открыть профиль в Web App"}</p>
        </div>
      ))}
    </main>
  );
}
