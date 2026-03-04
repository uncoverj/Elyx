"""Steam / CS2 stats via Steam Web API.

Requires STEAM_API_KEY env var for full access.
Falls back to public profile data if key is missing.
Usage: pass steam64 ID or vanity URL → returns CS2 stats.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

STEAM_API_BASE = "https://api.steampowered.com"
CS2_APP_ID = 730


@dataclass
class SteamCS2Stats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    hours_played: float | None = None
    source: str = "steam"
    verified: bool = True


CS2_RANKS = {
    range(0, 5000): "Silver",
    range(5000, 10000): "Gold Nova",
    range(10000, 15000): "Master Guardian",
    range(15000, 20000): "Legendary Eagle",
    range(20000, 25000): "Supreme",
    range(25000, 100000): "Global Elite",
}


def _rank_from_elo(elo: int | None) -> str | None:
    if elo is None:
        return None
    for r, name in CS2_RANKS.items():
        if elo in r:
            return name
    return None


async def _resolve_steam64(account_ref: str) -> str | None:
    """Resolve vanity URL or raw steam64 to a steam64 ID string."""
    cleaned = account_ref.strip().rstrip("/")
    vanity_name = None

    if cleaned.startswith("https://steamcommunity.com/"):
        parts = cleaned.split("/")
        if "id" in parts:
            idx = parts.index("id")
            if idx + 1 < len(parts):
                vanity_name = parts[idx + 1]
                cleaned = vanity_name
        elif "profiles" in parts:
            idx = parts.index("profiles")
            if idx + 1 < len(parts):
                cleaned = parts[idx + 1]

    if cleaned.isdigit() and len(cleaned) >= 10:
        return cleaned

    # Method 1: Try Steam Web API (requires key)
    settings = get_settings()
    steam_key = getattr(settings, "steam_api_key", "") or ""
    if steam_key:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v0001/",
                    params={"key": steam_key, "vanityurl": cleaned},
                )
                if resp.status_code == 200:
                    data = resp.json().get("response", {})
                    if data.get("success") == 1:
                        return data.get("steamid")
        except httpx.HTTPError:
            pass

    # Method 2: Try Steam community XML profile (no key needed)
    lookup_name = vanity_name or cleaned
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(
                f"https://steamcommunity.com/id/{lookup_name}/?xml=1",
            )
            if resp.status_code == 200:
                text = resp.text
                # Parse steamID64 from XML: <steamID64>76561198xxxxx</steamID64>
                import re
                match = re.search(r"<steamID64>(\d+)</steamID64>", text)
                if match:
                    return match.group(1)
    except httpx.HTTPError:
        pass

    return None


async def fetch_cs2_stats(account_ref: str) -> SteamCS2Stats | None:
    """Fetch CS2 stats for a Steam account."""
    settings = get_settings()
    steam_key = getattr(settings, "steam_api_key", "") or ""

    steam64 = await _resolve_steam64(account_ref)
    if not steam64:
        logger.warning("Could not resolve Steam ID: %s", account_ref)
        return None

    if not steam_key:
        logger.info("STEAM_API_KEY not set, returning partial stats for %s", steam64)
        return SteamCS2Stats(verified=False)

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            stats_resp = await client.get(
                f"{STEAM_API_BASE}/ISteamUserStats/GetUserStatsForGame/v0002/",
                params={"appid": CS2_APP_ID, "key": steam_key, "steamid": steam64},
            )

            kd = None
            winrate = None

            if stats_resp.status_code == 200:
                game_stats = stats_resp.json().get("playerstats", {}).get("stats", [])
                stats_map = {s["name"]: s["value"] for s in game_stats}

                total_kills = stats_map.get("total_kills", 0)
                total_deaths = stats_map.get("total_deaths", 1)
                total_wins = stats_map.get("total_wins", 0)
                total_rounds = stats_map.get("total_rounds_played", 0)

                if total_deaths > 0:
                    kd = round(total_kills / total_deaths, 2)
                if total_rounds > 0:
                    winrate = round(total_wins / total_rounds * 100, 1)

            games_resp = await client.get(
                f"{STEAM_API_BASE}/IPlayerService/GetOwnedGames/v0001/",
                params={
                    "key": steam_key,
                    "steamid": steam64,
                    "format": "json",
                    "include_appinfo": 0,
                },
            )

            hours_played = None
            if games_resp.status_code == 200:
                games = games_resp.json().get("response", {}).get("games", [])
                cs2 = next((g for g in games if g.get("appid") == CS2_APP_ID), None)
                if cs2:
                    minutes = cs2.get("playtime_forever", 0)
                    hours_played = round(minutes / 60, 1)

            return SteamCS2Stats(
                kd=kd,
                winrate=winrate,
                hours_played=hours_played,
            )

    except httpx.HTTPError as exc:
        logger.error("Steam API error for %s: %s", account_ref, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching CS2 stats for %s: %s", account_ref, exc)
        return None
