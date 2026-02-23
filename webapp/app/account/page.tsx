"use client";

import { FormEvent, useState } from "react";

import { backendFetch } from "@/lib/api";

export default function AccountPage() {
  const [riot, setRiot] = useState("");
  const [steam, setSteam] = useState("");
  const [result, setResult] = useState("");

  const submitRiot = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await backendFetch("/account/link/riot", {
        method: "POST",
        body: JSON.stringify({ account_ref: riot }),
      });
      setResult("Riot ID сохранен");
    } catch (err: any) {
      setResult("Ошибка Riot: " + err.message);
    }
  };

  const submitSteam = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await backendFetch("/account/link/steam", {
        method: "POST",
        body: JSON.stringify({ account_ref: steam }),
      });
      setResult("Steam ID сохранен");
    } catch (err: any) {
      setResult("Ошибка Steam: " + err.message);
    }
  };

  const refreshStats = async () => {
    const res = await backendFetch("/account/refresh-stats", { method: "POST" });
    setResult(res.message || "Обновлено");
  };

  return (
    <main className="card grid">
      <h1>Аккаунты</h1>
      <form onSubmit={submitRiot} className="grid">
        <label>Riot ID</label>
        <input value={riot} onChange={(e) => setRiot(e.target.value)} placeholder="name#tag" />
        <button className="button secondary" type="submit">
          Привязать Riot
        </button>
      </form>

      <form onSubmit={submitSteam} className="grid">
        <label>Steam</label>
        <input value={steam} onChange={(e) => setSteam(e.target.value)} placeholder="steam64 / vanity" />
        <button className="button secondary" type="submit">
          Привязать Steam
        </button>
      </form>

      <button className="button primary" onClick={refreshStats}>
        Refresh stats
      </button>

      {result && <p>{result}</p>}
    </main>
  );
}
