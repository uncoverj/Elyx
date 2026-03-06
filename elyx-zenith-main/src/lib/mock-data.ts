// Mock data for the Elyx tracker

export const playerProfile = {
  username: "Sygar",
  tag: "lovly",
  telegramUsername: "@sygar_val",
  trustScore: 85.24,
  likes: 52,
  dislikes: 9,
  currentRank: { tier: "Diamond", division: 1, rr: 67 },
  peakRank: { tier: "Ascendant", division: 2, rr: 89 },
  playtime: "55ч 25м",
  elyxScore: 847,
};

export const overviewStats = {
  damagePerRound: { value: 138.9, percentile: 46, label: "Damage/Round" },
  kdRatio: { value: 0.92, percentile: 30, label: "K/S Ratio" },
  headshotPct: { value: 30.1, percentile: 89, label: "Headshot %" },
  winPct: { value: 61.0, percentile: 89, label: "Win %" },
  wins: { value: 61, percentile: 92, label: "Wins" },
  kills: { value: 1485, percentile: 86, label: "Kills" },
  deaths: { value: 1620, percentile: 61, label: "Deaths" },
  aces: { value: 4, percentile: 95, label: "Aces" },
};

export const roles = [
  { name: "Duelist", matches: 58, winRate: 62.1, kd: 0.94, damagePerRound: 147.3, color: "hsl(0, 72%, 51%)" },
  { name: "Controller", matches: 41, winRate: 56.1, kd: 0.87, damagePerRound: 127.0, color: "hsl(210, 100%, 60%)" },
  { name: "Initiator", matches: 4, winRate: 75.0, kd: 1.22, damagePerRound: 137.7, color: "hsl(142, 71%, 45%)" },
  { name: "Sentinel", matches: 1, winRate: 100.0, kd: 0.94, damagePerRound: 130.5, color: "hsl(260, 80%, 60%)" },
];

export const topAgents = [
  { name: "Jett", role: "Duelist", games: 28, kd: 1.38, winRate: 62.0, playtime: "27ч 54м" },
  { name: "Neon", role: "Duelist", games: 17, kd: 1.21, winRate: 55.2, playtime: "15ч 11м" },
  { name: "Brimstone", role: "Controller", games: 12, kd: 0.96, winRate: 58.3, playtime: "10ч 5м" },
  { name: "Omen", role: "Controller", games: 8, kd: 0.96, winRate: 55.2, playtime: "6ч 30м" },
  { name: "Pearl", role: "Sentinel", games: 5, kd: 1.01, winRate: 78.9, playtime: "4ч 20м" },
];

export interface MatchData {
  id: string;
  date: string;
  dateLabel: string;
  score: string;
  won: boolean;
  agent: string;
  kda: string;
  kd: number;
  damagePerRound: number;
  map: string;
  mode: string;
  headshotPct?: number;
}

export const matches: MatchData[] = [
  { id: "1", date: "2026-02-24", dateLabel: "24 февр.", score: "12:14", won: false, agent: "Jett", kda: "14/25/13", kd: 0.6, damagePerRound: 121, map: "Corrode", mode: "Competitive" },
  { id: "2", date: "2026-02-24", dateLabel: "24 февр.", score: "13:8", won: true, agent: "Jett", kda: "16/16/6", kd: 1.0, damagePerRound: 142, map: "Bind", mode: "Competitive" },
  { id: "3", date: "2026-02-24", dateLabel: "24 февр.", score: "13:11", won: true, agent: "Neon", kda: "11/20/7", kd: 0.6, damagePerRound: 95, map: "Abbys", mode: "Competitive" },
  { id: "4", date: "2026-02-24", dateLabel: "24 февр.", score: "12:14", won: false, agent: "Brimstone", kda: "17/22/3", kd: 0.8, damagePerRound: 135, map: "Corrode", mode: "Competitive" },
  { id: "5", date: "2026-02-23", dateLabel: "23 февр.", score: "13:7", won: true, agent: "Jett", kda: "22/14/5", kd: 1.57, damagePerRound: 147, map: "Ascent", mode: "Competitive" },
  { id: "6", date: "2026-02-23", dateLabel: "23 февр.", score: "9:13", won: false, agent: "Neon", kda: "18/19/4", kd: 0.95, damagePerRound: 128, map: "Haven", mode: "Competitive" },
  { id: "7", date: "2026-02-23", dateLabel: "23 февр.", score: "13:5", won: true, agent: "Jett", kda: "25/10/8", kd: 2.50, damagePerRound: 178, map: "Bind", mode: "Competitive" },
  { id: "8", date: "2026-02-23", dateLabel: "23 февр.", score: "13:2", won: true, agent: "Neon", kda: "11/9/2", kd: 1.2, damagePerRound: 128, map: "Haven", mode: "Competitive" },
  { id: "9", date: "2026-02-23", dateLabel: "23 февр.", score: "5:13", won: false, agent: "Jett", kda: "9/14/5", kd: 0.6, damagePerRound: 111, map: "Breeze", mode: "Competitive" },
  { id: "10", date: "2026-02-23", dateLabel: "23 февр.", score: "13:5", won: true, agent: "Brimstone", kda: "12/12/1", kd: 1.0, damagePerRound: 114, map: "Corrode", mode: "Competitive" },
  { id: "11", date: "2026-02-22", dateLabel: "22 февр.", score: "10:13", won: false, agent: "Jett", kda: "8/16/2", kd: 0.5, damagePerRound: 75, map: "Haven", mode: "Competitive" },
  { id: "12", date: "2026-02-22", dateLabel: "22 февр.", score: "13:4", won: true, agent: "Neon", kda: "17/11/4", kd: 1.5, damagePerRound: 147, map: "Split", mode: "Competitive" },
];

export const leaderboardPlayers = [
  { rank: 1, username: "QOR twitch Smoke", trust: 94.64, rating: 1003, tier: "Radiant" },
  { rank: 2, username: "EP kozzy", trust: 96.56, rating: 976, tier: "Radiant" },
  { rank: 3, username: "T1 Satoru", trust: 91.07, rating: 965, tier: "Radiant" },
  { rank: 4, username: "KRU dante", trust: 95.78, rating: 940, tier: "Radiant" },
  { rank: 5, username: "MercureFPS", trust: 87.92, rating: 931, tier: "Radiant" },
  { rank: 6, username: "GL hAwksinho", trust: 90.12, rating: 905, tier: "Radiant" },
  { rank: 7, username: "MISA BadreX", trust: 74.55, rating: 900, tier: "Radiant" },
  { rank: 8, username: "lorem", trust: 54.88, rating: 856, tier: "Radiant" },
  { rank: 9, username: "Frost_Nova", trust: 88.32, rating: 845, tier: "Immortal 3" },
  { rank: 10, username: "ShadowKill99", trust: 79.21, rating: 832, tier: "Immortal 3" },
  { rank: 11, username: "VenomStrike", trust: 92.10, rating: 821, tier: "Immortal 3" },
  { rank: 12, username: "NightHawk", trust: 85.45, rating: 810, tier: "Immortal 2" },
  { rank: 13, username: "BlazeFury", trust: 77.88, rating: 798, tier: "Immortal 2" },
  { rank: 14, username: "CyberVortex", trust: 91.33, rating: 785, tier: "Immortal 1" },
  { rank: 15, username: "PhantomAce", trust: 83.67, rating: 772, tier: "Immortal 1" },
];

export const rankDistribution = [
  { rank: "I", label: "Iron", count: 2, pct: 3 },
  { rank: "B", label: "Bronze", count: 5, pct: 8 },
  { rank: "S", label: "Silver", count: 8, pct: 12 },
  { rank: "G", label: "Gold", count: 6, pct: 9 },
  { rank: "P", label: "Platinum", count: 4, pct: 6 },
  { rank: "D", label: "Diamond", count: 3, pct: 5 },
  { rank: "A", label: "Ascendant", count: 2, pct: 3 },
  { rank: "I3", label: "Immortal", count: 1, pct: 2 },
  { rank: "R", label: "Radiant", count: 1, pct: 1 },
];

export const connectedAccounts = [
  { platform: "Riot Games", username: "Sygar#lovly", games: "Valorant и LoL", connected: true },
  { platform: "Steam", username: "Prosto_lol33", games: "CS2", connected: true },
  { platform: "Faceit", username: "", games: "CS2 Faceit", connected: false },
  { platform: "Epic Games", username: "", games: "Fortnite", connected: false },
];

export const gameOptions = [
  { id: "valorant", name: "VALORANT", active: true },
  { id: "cs2", name: "Counter-Strike 2", active: false },
  { id: "lol", name: "League of Legends", active: false },
  { id: "dota2", name: "Dota 2", active: false },
  { id: "fortnite", name: "Fortnite", active: false },
];
