"""Overwatch 2 stats via OverFast API (https://overfast-api.tekrop.fr/).

Free, no API key needed. Rate limit: ~30 req/min.
Usage: pass BattleTag like "Name#1234" or "Name-1234" → returns rank, winrate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OVERFAST_BASE = "https://overfast-api.tekrop.fr"


@dataclass
class OW2Stats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    source: str = "blizzard"
    verified: bool = True


async def fetch_ow2_stats(battletag: str) -> OW2Stats | None:
    """Fetch Overwatch 2 stats for a BattleTag like 'Name#1234'."""
    cleaned = battletag.strip().replace("#", "-")
    if not cleaned:
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            summary_resp = await client.get(f"{OVERFAST_BASE}/players/{cleaned}/summary")

            if summary_resp.status_code == 404:
                logger.warning("OW2 player not found: %s", battletag)
                return None

            if summary_resp.status_code != 200:
                logger.warning("OW2 API error %d for %s", summary_resp.status_code, battletag)
                return None

            data = summary_resp.json()

            rank_name = None
            rank_icon = None
            competitive = data.get("competitive")
            if competitive:
                pc = competitive.get("pc")
                if pc:
                    for role_key in ("tank", "damage", "support"):
                        role_data = pc.get(role_key)
                        if role_data and role_data.get("division"):
                            division = role_data["division"]
                            tier = role_data.get("tier", "")
                            rank_name = f"{division.capitalize()} {tier}" if tier else division.capitalize()
                            break

            total_stats = data.get("stats", {})
            games_won = total_stats.get("games_won")
            games_played = total_stats.get("games_played")

            winrate = None
            if games_won and games_played and games_played > 0:
                winrate = round(games_won / games_played * 100, 1)

            kd = None
            kd_ratio = total_stats.get("kd_ratio")
            if kd_ratio:
                kd = round(kd_ratio, 2)

            return OW2Stats(
                rank_name=rank_name,
                kd=kd,
                winrate=winrate,
            )

    except httpx.HTTPError as exc:
        logger.error("OW2 API error for %s: %s", battletag, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching OW2 stats for %s: %s", battletag, exc)
        return None
