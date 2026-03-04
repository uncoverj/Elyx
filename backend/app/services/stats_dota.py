"""Dota 2 stats via OpenDota API (https://docs.opendota.com/).

Free tier: no key needed, 60 req/min.
Usage: pass Steam ID (steam64 or vanity) → returns MMR, K/D, win rate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OPENDOTA_BASE = "https://api.opendota.com/api"

MEDAL_RANKS = {
    1: "Herald",
    2: "Guardian",
    3: "Crusader",
    4: "Archon",
    5: "Legend",
    6: "Ancient",
    7: "Divine",
    8: "Immortal",
}


@dataclass
class DotaStats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    source: str = "steam"
    verified: bool = True


def _medal_from_tier(rank_tier: int | None) -> str | None:
    if not rank_tier:
        return None
    medal = rank_tier // 10
    stars = rank_tier % 10
    base = MEDAL_RANKS.get(medal)
    if not base:
        return None
    return f"{base} {stars}" if stars else base


async def _resolve_steam_id(account_ref: str) -> str | None:
    """Try to resolve a vanity URL or steam64 to a steam32 account ID."""
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
        steam32 = int(cleaned) - 76561197960265728
        if steam32 > 0:
            return str(steam32)

    if cleaned.isdigit():
        return cleaned

    # Method 1: OpenDota search
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{OPENDOTA_BASE}/search", params={"q": cleaned})
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    return str(results[0].get("account_id"))
    except httpx.HTTPError:
        pass

    # Method 2: Steam community XML (no key needed) → convert to steam32
    lookup_name = vanity_name or cleaned
    try:
        import re
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(
                f"https://steamcommunity.com/id/{lookup_name}/?xml=1",
            )
            if resp.status_code == 200:
                match = re.search(r"<steamID64>(\d+)</steamID64>", resp.text)
                if match:
                    steam64 = int(match.group(1))
                    steam32 = steam64 - 76561197960265728
                    if steam32 > 0:
                        return str(steam32)
    except httpx.HTTPError:
        pass

    return None


async def fetch_dota_stats(account_ref: str) -> DotaStats | None:
    """Fetch Dota 2 stats for a Steam account (steam64, steam32, or vanity name)."""
    account_id = await _resolve_steam_id(account_ref)
    if not account_id:
        logger.warning("Could not resolve Steam account: %s", account_ref)
        return None

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            profile_resp = await client.get(f"{OPENDOTA_BASE}/players/{account_id}")
            if profile_resp.status_code != 200:
                logger.warning("OpenDota player not found: %s", account_id)
                return None

            profile = profile_resp.json()
            rank_tier = profile.get("rank_tier")
            mmr = profile.get("mmr_estimate", {}).get("estimate")

            rank_name = _medal_from_tier(rank_tier)

            wl_resp = await client.get(f"{OPENDOTA_BASE}/players/{account_id}/wl")
            winrate = None
            if wl_resp.status_code == 200:
                wl = wl_resp.json()
                wins = wl.get("win", 0)
                losses = wl.get("lose", 0)
                total = wins + losses
                if total > 0:
                    winrate = round(wins / total * 100, 1)

            kd = None
            totals_resp = await client.get(
                f"{OPENDOTA_BASE}/players/{account_id}/totals",
            )
            if totals_resp.status_code == 200:
                totals = totals_resp.json()
                kills_entry = next((t for t in totals if t.get("field") == "kills"), None)
                deaths_entry = next((t for t in totals if t.get("field") == "deaths"), None)
                if kills_entry and deaths_entry:
                    n = kills_entry.get("n", 0)
                    total_kills = kills_entry.get("sum", 0)
                    total_deaths = deaths_entry.get("sum", 1)
                    if n > 0 and total_deaths > 0:
                        kd = round(total_kills / total_deaths, 2)

            return DotaStats(
                rank_name=rank_name,
                rank_points=mmr,
                kd=kd,
                winrate=winrate,
            )

    except httpx.HTTPError as exc:
        logger.error("OpenDota API error for %s: %s", account_ref, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching Dota stats for %s: %s", account_ref, exc)
        return None
