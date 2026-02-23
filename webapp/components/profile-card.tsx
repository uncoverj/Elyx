type Stats = {
  kd?: number | null;
  winrate?: number | null;
  rank_name?: string | null;
};

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
  stats?: Stats | null;
};

export default function ProfileCard({ profile }: { profile: Profile }) {
  return (
    <div className="card grid">
      <h2>{profile.nickname}</h2>
      <p>
        {profile.age} • {profile.gender} • {profile.game_name}
      </p>
      <p>Roles: {profile.roles?.join(", ") || "-"}</p>
      <p>Tags: {profile.tags?.join(", ") || "-"}</p>
      <p>
        Rank: {profile.stats?.rank_name || "-"} | KD: {profile.stats?.kd ?? "-"} | WR: {profile.stats?.winrate ?? "-"}
      </p>
      <p>
        Trust: 👍 {profile.trust_up} | 🗑 {profile.trust_down}
      </p>
      <p>{profile.bio}</p>
    </div>
  );
}
