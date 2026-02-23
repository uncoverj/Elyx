"use client";

import { FormEvent, useEffect, useState } from "react";

import { backendFetch } from "@/lib/api";

type Game = { id: number; name: string };

type FormState = {
  nickname: string;
  gender: string;
  age: number;
  game_id: number;
  bio: string;
  roles: string;
  tags: string;
  media_type: string;
  media_file_id: string;
};

export default function EditProfilePage() {
  const [games, setGames] = useState<Game[]>([]);
  const [message, setMessage] = useState("");
  const [form, setForm] = useState<FormState>({
    nickname: "",
    gender: "other",
    age: 18,
    game_id: 0,
    bio: "",
    roles: "",
    tags: "",
    media_type: "photo",
    media_file_id: "update_via_bot",
  });

  useEffect(() => {
    const run = async () => {
      const gamesRes = await backendFetch("/games");
      setGames(gamesRes);
      if (gamesRes[0]) {
        setForm((prev) => ({ ...prev, game_id: gamesRes[0].id }));
      }

      try {
        const me = await backendFetch("/profiles/me");
        setForm({
          nickname: me.nickname,
          gender: me.gender,
          age: me.age,
          game_id: me.game_id,
          bio: me.bio,
          roles: (me.roles || []).join(", "),
          tags: (me.tags || []).join(", "),
          media_type: me.media_type,
          media_file_id: me.media_file_id,
        });
      } catch {
        // profile absent is fine
      }
    };
    run();
  }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setMessage("");

    try {
      await backendFetch("/profiles/me", {
        method: "PUT",
        body: JSON.stringify({
          nickname: form.nickname,
          gender: form.gender,
          age: Number(form.age),
          game_id: Number(form.game_id),
          bio: form.bio,
          media_type: form.media_type,
          media_file_id: form.media_file_id,
          roles: form.roles
            .split(",")
            .map((x) => x.trim())
            .filter(Boolean),
          tags: form.tags
            .split(",")
            .map((x) => x.trim().toLowerCase())
            .filter(Boolean),
        }),
      });
      setMessage("Профиль сохранен ✅");
    } catch (err: any) {
      setMessage("Ошибка: " + err.message);
    }
  };

  return (
    <main className="card">
      <h1>Редактирование профиля</h1>
      <p>Медиа загружай через бота. Здесь можно обновить текстовые поля.</p>
      <form className="grid" onSubmit={submit}>
        <input value={form.nickname} onChange={(e) => setForm({ ...form, nickname: e.target.value })} placeholder="Nickname" required />

        <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>

        <input type="number" min={13} max={99} value={form.age} onChange={(e) => setForm({ ...form, age: Number(e.target.value) })} />

        <select value={form.game_id} onChange={(e) => setForm({ ...form, game_id: Number(e.target.value) })}>
          {games.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>

        <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} placeholder="Bio" rows={5} />
        <input value={form.roles} onChange={(e) => setForm({ ...form, roles: e.target.value })} placeholder="Roles, comma separated" />
        <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="Tags, comma separated" />

        <button className="button primary" type="submit">
          Сохранить
        </button>
      </form>
      {message && <p>{message}</p>}
    </main>
  );
}
