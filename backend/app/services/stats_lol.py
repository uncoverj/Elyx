"""League of Legends stats via Riot Games API.

Flow:
1. Riot ID "Name#Tag" → PUUID via account-v1 (routing: europe → americas → asia)
2. PUUID → summoner via summoner-v4 (try each LoL server until found)
3. Summoner ID → ranked entries via league-v4
4. PUUID → recent match IDs via match-v5 → K/D from match details

Requires RIOT_API_KEY env var (get one at https://developer.riotgames.com/).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Riot Account API uses routing values (NOT per-game regions).
# Accounts are global — any routing value will find any account.
ACCOUNT_ROUTING_VALUES = [
    "https://europe.api.riotgames.com",
    "https://americas.api.riotgames.com",
    "https://asia.api.riotgames.com",
]

# Per-game LoL servers to find summoner data
LOL_SERVERS = {
    "euw1": "https://euw1.api.riotgames.com",
    "eun1": "https://eun1.api.riotgames.com",
    "na1": "https://na1.api.riotgames.com",
    "kr": "https://kr.api.riotgames.com",
    "br1": "https://br1.api.riotgames.com",
    "tr1": "https://tr1.api.riotgames.com",
    "ru": "https://ru.api.riotgames.com",
    "oc1": "https://oc1.api.riotgames.com",
    "la1": "https://la1.api.riotgames.com",
    "la2": "https://la2.api.riotgames.com",
    "jp1": "https://jp1.api.riotgames.com",
}

# Map LoL server → match-v5 routing value
SERVER_TO_MATCH_ROUTING = {
    "euw1": "https://europe.api.riotgames.com",
    "eun1": "https://europe.api.riotgames.com",
    "tr1": "https://europe.api.riotgames.com",
    "ru": "https://europe.api.riotgames.com",
    "na1": "https://americas.api.riotgames.com",
    "br1": "https://americas.api.riotgames.com",
    "la1": "https://americas.api.riotgames.com",
    "la2": "https://americas.api.riotgames.com",
    "kr": "https://asia.api.riotgames.com",
    "jp1": "https://asia.api.riotgames.com",
    "oc1": "https://asia.api.riotgames.com",
}


@dataclass
class LoLStats:
    rank_name: str | None = None
    rank_points: int | None = None
    kd: float | None = None
    winrate: float | None = None
    source: str = "riot"
    verified: bool = True


def _format_rank(tier: str, rank: str) -> str:
    return f"{tier.capitalize()} {rank}"


async def _get_puuid(client: httpx.AsyncClient, name: str, tag: str, headers: dict) -> str | None:
    """Get PUUID via Riot Account API. Try each routing value."""
    for base in ACCOUNT_ROUTING_VALUES:
        try:
            resp = await client.get(
                f"{base}/riot/account/v1/accounts/by-riot-id/{name}/{tag}",
                headers=headers,
            )
            if resp.status_code == 200:
                puuid = resp.json().get("puuid")
                if puuid:
                    logger.info("Found Riot PUUID for %s#%s via %s", name, tag, base.split("//")[1].split(".")[0])
                    return puuid
            elif resp.status_code == 403:
                logger.error("Riot API key invalid or expired (403)")
                return None
            elif resp.status_code == 404:
                continue
        except httpx.HTTPError:
            continue
    return None


async def _find_summoner(client: httpx.AsyncClient, puuid: str, headers: dict) -> tuple[dict | None, str | None]:
    """Find LoL summoner by PUUID across all servers. Returns (summoner_data, server_key)."""
    for server_key, base in LOL_SERVERS.items():
        try:
            resp = await client.get(
                f"{base}/lol/summoner/v4/summoners/by-puuid/{puuid}",
                headers=headers,
            )
            if resp.status_code == 200:
                logger.info("Found LoL summoner on server: %s", server_key)
                return resp.json(), server_key
            elif resp.status_code == 404:
                continue
        except httpx.HTTPError:
            continue
    return None, None


async def _get_ranked_data(client: httpx.AsyncClient, server_key: str, summoner_id: str, headers: dict) -> tuple[str | None, int | None, float | None]:
    """Get ranked data (rank, LP, winrate) from league-v4."""
    base = LOL_SERVERS.get(server_key)
    if not base:
        return None, None, None

    try:
        resp = await client.get(
            f"{base}/lol/league/v4/entries/by-summoner/{summoner_id}",
            headers=headers,
        )
        if resp.status_code != 200:
            return None, None, None

        entries = resp.json()
        solo_q = next((e for e in entries if e.get("queueType") == "RANKED_SOLO_5x5"), None)
        if not solo_q:
            solo_q = next((e for e in entries if e.get("queueType") == "RANKED_FLEX_SR"), None)

        if not solo_q:
            return None, None, None

        tier = solo_q.get("tier", "")
        rank = solo_q.get("rank", "")
        lp = solo_q.get("leaguePoints", 0)
        wins = solo_q.get("wins", 0)
        losses = solo_q.get("losses", 0)

        rank_name = _format_rank(tier, rank) if tier else None
        total_games = wins + losses
        winrate = round(wins / total_games * 100, 1) if total_games > 0 else None

        return rank_name, lp, winrate
    except httpx.HTTPError:
        return None, None, None


async def _get_kd_from_matches(client: httpx.AsyncClient, server_key: str, puuid: str, headers: dict) -> float | None:
    """Get average K/D from recent ranked matches via match-v5."""
    match_base = SERVER_TO_MATCH_ROUTING.get(server_key)
    if not match_base:
        return None

    try:
        # Get recent match IDs
        ids_resp = await client.get(
            f"{match_base}/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params={"queue": 420, "count": 10},  # 420 = ranked solo
            headers=headers,
        )
        if ids_resp.status_code != 200:
            return None

        match_ids = ids_resp.json()
        if not match_ids:
            return None

        total_kills = 0
        total_deaths = 0
        total_assists = 0
        count = 0

        # Fetch up to 5 match details (to avoid rate limits)
        for match_id in match_ids[:5]:
            try:
                detail_resp = await client.get(
                    f"{match_base}/lol/match/v5/matches/{match_id}",
                    headers=headers,
                )
                if detail_resp.status_code != 200:
                    continue

                info = detail_resp.json().get("info", {})
                participants = info.get("participants", [])
                for p in participants:
                    if p.get("puuid") == puuid:
                        total_kills += p.get("kills", 0)
                        total_deaths += p.get("deaths", 0)
                        total_assists += p.get("assists", 0)
                        count += 1
                        break
            except httpx.HTTPError:
                continue

        if count > 0 and total_deaths > 0:
            return round((total_kills + total_assists * 0.5) / total_deaths, 2)
        return None
    except httpx.HTTPError:
        return None


async def fetch_lol_stats(riot_id: str) -> LoLStats | None:
    """Fetch LoL ranked stats for a Riot ID like 'Name#Tag'."""
    settings = get_settings()
    api_key = settings.riot_api_key
    if not api_key:
        logger.info("RIOT_API_KEY not set, skipping LoL stats")
        return None

    parts = riot_id.replace(" ", "").split("#")
    if len(parts) != 2:
        logger.warning("Invalid Riot ID format: %s (expected Name#Tag)", riot_id)
        return None

    name, tag = parts[0], parts[1]
    headers = {"X-Riot-Token": api_key}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # Step 1: Get PUUID (global lookup)
            puuid = await _get_puuid(client, name, tag, headers)
            if not puuid:
                logger.warning("Riot account not found: %s#%s", name, tag)
                return None

            # Step 2: Find summoner on a LoL server
            summoner, server_key = await _find_summoner(client, puuid, headers)
            if not summoner or not server_key:
                logger.warning("LoL summoner not found for PUUID on any server")
                return LoLStats()  # Account exists but no LoL data

            summoner_id = summoner.get("id")

            # Step 3: Get ranked data
            rank_name, lp, winrate = await _get_ranked_data(client, server_key, summoner_id, headers)

            # Step 4: Get K/D from recent matches
            kd = await _get_kd_from_matches(client, server_key, puuid, headers)

            return LoLStats(
                rank_name=rank_name,
                rank_points=lp,
                kd=kd,
                winrate=winrate,
            )

    except httpx.HTTPError as exc:
        logger.error("Riot API error for %s: %s", riot_id, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error fetching LoL stats for %s: %s", riot_id, exc)
        return None
