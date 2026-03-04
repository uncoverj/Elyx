"""Valorant stats via Henrik's unofficial Valorant API (https://docs.henrikdev.xyz/).

Flow:
1. /v1/account/{name}/{tag} → auto-detect region + get PUUID
2. /v2/mmr/{region}/{name}/{tag} → rank, RR, ELO
3. /v3/matches/{region}/{name}/{tag} → K/D, winrate from competitive matches

If HENRIK_API_KEY is set in .env, sends it as Authorization header (higher rate limit).
Free tier works without key but limited to ~30 req/min.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

HENRIK_BASE = "https://api.henrikdev.xyz/valorant"
ALL_REGIONS = ["eu", "na", "ap", "kr", "br", "latam"]


@dataclass
class ValorantStats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    source: str = "riot"
    verified: bool = True


def _henrik_headers() -> dict[str, str]:
    """Build headers with optional API key."""
    settings = get_settings()
    key = settings.henrik_api_key
    headers: dict[str, str] = {"Accept": "application/json"}
    if key:
        headers["Authorization"] = key
    return headers


async def _detect_region(client: httpx.AsyncClient, name: str, tag: str, headers: dict) -> str | None:
    """Use Henrik /v1/account to auto-detect player region."""
    try:
        resp = await client.get(f"{HENRIK_BASE}/v1/account/{name}/{tag}", headers=headers)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            region = data.get("region")
            if region:
                logger.info("Detected Valorant region for %s#%s: %s", name, tag, region)
                return region.lower()
        elif resp.status_code == 401:
            logger.error("Henrik API requires authentication. Set HENRIK_API_KEY in .env. Get one at https://docs.henrikdev.xyz/")
            return None
    except Exception as exc:
        logger.debug("Region detection failed: %s", exc)
    return None


async def _fetch_mmr(client: httpx.AsyncClient, region: str, name: str, tag: str, headers: dict) -> tuple[str | None, int | None]:
    """Fetch MMR data, returns (rank_name, rank_points)."""
    resp = await client.get(f"{HENRIK_BASE}/v2/mmr/{region}/{name}/{tag}", headers=headers)
    if resp.status_code == 200:
        data = resp.json().get("data", {})
        current = data.get("current_data", {})
        rank_name = current.get("currenttierpatched")
        rr = current.get("ranking_in_tier")
        elo = current.get("elo")
        # Use ELO as rank_points if available (more useful than RR for scoring)
        rank_points = elo if elo else rr
        return rank_name, rank_points
    logger.debug("MMR fetch for %s/%s#%s returned %d", region, name, tag, resp.status_code)
    return None, None


async def _fetch_match_stats(client: httpx.AsyncClient, region: str, name: str, tag: str, headers: dict) -> tuple[float | None, float | None]:
    """Fetch K/D and winrate from recent competitive matches."""
    resp = await client.get(
        f"{HENRIK_BASE}/v3/matches/{region}/{name}/{tag}",
        params={"size": 10, "filter": "competitive"},
        headers=headers,
    )
    if resp.status_code != 200:
        logger.debug("Matches fetch for %s/%s#%s returned %d", region, name, tag, resp.status_code)
        return None, None

    matches = resp.json().get("data", [])
    if not matches:
        return None, None

    total_kills = 0
    total_deaths = 0
    wins = 0
    matched_games = 0

    for match in matches:
        players = match.get("players", {}).get("all_players", [])
        for player in players:
            p_name = player.get("name", "").lower()
            p_tag = player.get("tag", "").lower()
            if p_name == name.lower() and p_tag == tag.lower():
                stats = player.get("stats", {})
                total_kills += stats.get("kills", 0)
                total_deaths += stats.get("deaths", 0)
                matched_games += 1

                team = player.get("team", "").lower()
                teams = match.get("teams", {})
                team_data = teams.get(team, {})
                if team_data.get("has_won"):
                    wins += 1
                break

    kd = round(total_kills / max(total_deaths, 1), 2) if matched_games > 0 else None
    winrate = round(wins / matched_games * 100, 1) if matched_games > 0 else None
    return kd, winrate


async def fetch_valorant_stats(riot_id: str) -> ValorantStats | None:
    """Fetch Valorant MMR + match stats for a Riot ID like 'Name#Tag'."""
    parts = riot_id.replace(" ", "").split("#")
    if len(parts) != 2:
        logger.warning("Invalid Riot ID format: %s (expected Name#Tag)", riot_id)
        return None

    name, tag = parts[0], parts[1]
    headers = _henrik_headers()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: Auto-detect region
            region = await _detect_region(client, name, tag, headers)

            # Step 2: Fetch MMR
            rank_name = None
            rank_points = None

            if region:
                rank_name, rank_points = await _fetch_mmr(client, region, name, tag, headers)

            # Fallback: try all regions if auto-detect failed or MMR not found
            if not rank_name:
                for r in ALL_REGIONS:
                    if r == region:
                        continue
                    rank_name, rank_points = await _fetch_mmr(client, r, name, tag, headers)
                    if rank_name:
                        region = r
                        break

            # Use detected region or default to eu for matches
            match_region = region or "eu"

            # Step 3: Fetch K/D and winrate from matches
            kd, winrate = await _fetch_match_stats(client, match_region, name, tag, headers)

            if not rank_name and kd is None and winrate is None:
                logger.warning("No Valorant data found for %s#%s in any region", name, tag)
                return None

            return ValorantStats(
                rank_name=rank_name,
                rank_points=rank_points,
                kd=kd,
                winrate=winrate,
            )

    except httpx.HTTPError as exc:
        logger.error("Valorant API error for %s: %s", riot_id, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching Valorant stats for %s: %s", riot_id, exc)
        return None
