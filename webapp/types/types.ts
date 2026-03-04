// Shared types for the Elyx webapp

export interface UserProfile {
  user_id: number;
  tg_id: number;
  username: string | null;
  nickname: string;
  gender: string;
  age: number;
  game_id: number;
  game_name: string;
  bio: string;
  media_type: string;
  media_file_id: string;
  roles: string[];
  tags: string[];
  green_flags: string[];
  dealbreaker: string | null;
  mood_status: string | null;
  trust_up: number;
  trust_down: number;
  trust_score: number;
  is_premium: boolean;
  stats: UserStats | null;
}

export interface UserStats {
  kd: number | null;
  winrate: number | null;
  rank_name: string | null;
  rank_points: number | null;
  unified_score: number;
  source: string;
  source_status: string;
  verified: boolean;
}

export interface RoleBreakdown {
  role: string;
  icon: string;
  matches: number;
  winrate: number;
  kd: number;
  damage_round: number;
}

export interface AgentStats {
  name: string;
  icon: string;
  playtime: string;
  winrate: number;
  kd: number;
  damage_round: number;
}

export interface MapStats {
  name: string;
  thumbnail: string;
  wins: number;
  losses: number;
  winrate: number;
  kd: number;
}

export interface MatchEntry {
  id: number;
  agent: string;
  agent_icon: string;
  kills: number;
  deaths: number;
  assists: number;
  kd: number;
  won: boolean;
  map: string;
  mode: string;
  damage_round: number;
  date: string;
}

export interface DayGroup {
  date: string;
  avg_kd: number;
  avg_damage: number;
  avg_acs: number;
  match_count: number;
  matches: MatchEntry[];
}

export interface LeaderboardUser {
  position: number;
  user_id: number;
  nickname: string;
  trust_score: number;
  rating: number;
  tier: string;
}

export interface ExternalAccountInfo {
  provider: string;
  account_ref: string;
  verified: boolean;
}

export interface GameInfo {
  id: number;
  name: string;
}
