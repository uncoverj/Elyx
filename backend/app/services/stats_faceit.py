"""Faceit CS2 stats via Faceit Data API v4.

Uses FACEIT_API_KEY from .env for authentication.
Usage: pass Faceit nickname → returns ELO, level, K/D, win rate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

FACEIT_API_BASE = "https://open.faceit.com/data/v4"


@dataclass
class FaceitCS2Stats:
    rank_name: str | None = None
    rank_points: int | None = None  # ELO
    kd: float | None = None
    winrate: float | None = None
    faceit_level: int | None = None
    source: str = "faceit"
    verified: bool = True


FACEIT_LEVELS = {
    1: "Level 1", 2: "Level 2", 3: "Level 3", 4: "Level 4", 5: "Level 5",
    6: "Level 6", 7: "Level 7", 8: "Level 8", 9: "Level 9", 10: "Level 10",
}


async def fetch_faceit_stats(nickname: str) -> FaceitCS2Stats | None:
    """Fetch CS2 stats from Faceit by player nickname."""
    settings = get_settings()
    api_key = settings.faceit_api_key
    if not api_key:
        logger.warning("FACEIT_API_KEY not set, cannot fetch Faceit stats")
        return None

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            # Step 1: Get player info by nickname
            player_resp = await client.get(
                f"{FACEIT_API_BASE}/players",
                params={"nickname": nickname, "game": "cs2"},
                headers=headers,
            )

            if player_resp.status_code != 200:
                logger.warning("Faceit player lookup failed for '%s': %s", nickname, player_resp.status_code)
                return None

            player_data = player_resp.json()
            player_id = player_data.get("player_id")
            if not player_id:
                return None

            # Extract ELO and level from games.cs2
            games = player_data.get("games", {})
            cs2_data = games.get("cs2", {})
            elo = cs2_data.get("faceit_elo")
            level = cs2_data.get("skill_level")
            rank_name = FACEIT_LEVELS.get(level, f"Level {level}") if level else None

            # Step 2: Get lifetime stats for CS2
            stats_resp = await client.get(
                f"{FACEIT_API_BASE}/players/{player_id}/stats/cs2",
                headers=headers,
            )

            kd = None
            winrate = None

            if stats_resp.status_code == 200:
                stats_data = stats_resp.json()
                lifetime = stats_data.get("lifetime", {})

                kd_str = lifetime.get("Average K/D Ratio")
                if kd_str:
                    try:
                        kd = round(float(kd_str), 2)
                    except ValueError:
                        pass

                winrate_str = lifetime.get("Win Rate %")
                if winrate_str:
                    try:
                        winrate = round(float(winrate_str), 1)
                    except ValueError:
                        pass

            return FaceitCS2Stats(
                rank_name=rank_name,
                rank_points=int(elo) if elo else None,
                kd=kd,
                winrate=winrate,
                faceit_level=level,
            )

    except httpx.HTTPError as exc:
        logger.error("Faceit API error for '%s': %s", nickname, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching Faceit stats for '%s': %s", nickname, exc)
        return None
