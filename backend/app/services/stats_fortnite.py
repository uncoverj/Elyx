"""Fortnite stats via Fortnite-API.com (https://fortnite-api.com/).

Free tier: no key needed for stats lookup.
Usage: pass Epic username → returns K/D, win rate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

FORTNITE_API_BASE = "https://fortnite-api.com/v2"


@dataclass
class FortniteStats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    source: str = "epic"
    verified: bool = True


async def fetch_fortnite_stats(epic_name: str) -> FortniteStats | None:
    """Fetch Fortnite stats for an Epic Games username."""
    if not epic_name or len(epic_name) < 2:
        return None

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                f"{FORTNITE_API_BASE}/stats/br/v2",
                params={"name": epic_name, "accountType": "epic"},
            )

            if resp.status_code == 404:
                logger.warning("Fortnite player not found: %s", epic_name)
                return None

            if resp.status_code == 403:
                logger.warning("Fortnite stats are private for: %s", epic_name)
                return FortniteStats(verified=False)

            if resp.status_code != 200:
                logger.warning("Fortnite API error %d for %s", resp.status_code, epic_name)
                return None

            data = resp.json().get("data", {})
            stats = data.get("stats", {})
            overall = stats.get("all", {}).get("overall")

            if not overall:
                return FortniteStats()

            kills = overall.get("kills", 0)
            deaths = overall.get("deaths", 1)
            wins = overall.get("wins", 0)
            matches = overall.get("matches", 0)

            kd = round(kills / deaths, 2) if deaths > 0 else None
            winrate = round(wins / matches * 100, 1) if matches > 0 else None

            return FortniteStats(
                kd=kd,
                winrate=winrate,
            )

    except httpx.HTTPError as exc:
        logger.error("Fortnite API error for %s: %s", epic_name, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching Fortnite stats for %s: %s", epic_name, exc)
        return None
