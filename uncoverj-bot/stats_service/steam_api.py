"""
Клиент Steam Web API для получения статистики CS2 и Dota 2.
"""
import requests
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

STEAM_API_BASE = "https://api.steampowered.com"

# App IDs
CS2_APP_ID = 730
DOTA2_APP_ID = 570


def _get_steam_key() -> str | None:
    if settings.steam_api_key:
        return settings.steam_api_key.get_secret_value()
    return None


def fetch_steam_player_summary(steam_id: str) -> dict | None:
    """Получить базовую информацию об игроке Steam"""
    key = _get_steam_key()
    if not key:
        logger.error("Steam API key not configured")
        return None

    url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": key, "steamids": steam_id}

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            players = resp.json().get("response", {}).get("players", [])
            if players:
                return players[0]
        return None
    except requests.RequestException as e:
        logger.error(f"Steam API error: {e}")
        return None


def fetch_cs2_stats(steam_id: str) -> dict | None:
    """
    Получить статистику CS2 через Steam API.
    Возвращает dict с kills, deaths, wins, matches и т.д.
    """
    key = _get_steam_key()
    if not key:
        return None

    url = f"{STEAM_API_BASE}/ISteamUserStats/GetUserStatsForGame/v2/"
    params = {"key": key, "steamid": steam_id, "appid": CS2_APP_ID}

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            stats_list = resp.json().get("playerstats", {}).get("stats", [])
            stats_dict = {s["name"]: s["value"] for s in stats_list}

            total_kills = stats_dict.get("total_kills", 0)
            total_deaths = stats_dict.get("total_deaths", 1)
            total_wins = stats_dict.get("total_wins", 0)
            total_rounds = stats_dict.get("total_rounds_played", 1)
            total_matches = stats_dict.get("total_matches_played", 0)

            return {
                "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
                "winrate": round(total_wins / max(total_rounds, 1), 3),
                "matches_played": total_matches,
            }
        elif resp.status_code == 403:
            # Профиль закрыт
            logger.warning(f"CS2 profile is private for steam_id={steam_id}")
            return {"source_status": "private"}
        else:
            return None
    except requests.RequestException as e:
        logger.error(f"Steam CS2 stats error: {e}")
        return None


def fetch_dota2_stats(steam_id: str) -> dict | None:
    """
    Получить статистику Dota 2.
    Используем OpenDota API (бесплатный, без ключа) для расширенных данных.
    """
    # Конвертируем Steam64 ID в account_id
    try:
        account_id = int(steam_id) - 76561197960265728
    except (ValueError, TypeError):
        logger.error(f"Invalid steam_id for Dota 2: {steam_id}")
        return None

    url = f"https://api.opendota.com/api/players/{account_id}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json()
        mmr_estimate = data.get("mmr_estimate", {}).get("estimate", 0)
        rank_tier = data.get("rank_tier")  # Например, 53 = Legend 3

        # Получаем win/loss
        wl_url = f"https://api.opendota.com/api/players/{account_id}/wl"
        wl_resp = requests.get(wl_url, timeout=10)
        wins = 0
        losses = 0
        if wl_resp.status_code == 200:
            wl_data = wl_resp.json()
            wins = wl_data.get("win", 0)
            losses = wl_data.get("lose", 0)

        total = wins + losses

        return {
            "mmr": mmr_estimate,
            "rank_tier": rank_tier,
            "kd_ratio": None,  # Dota не имеет прямого K/D
            "winrate": round(wins / max(total, 1), 3),
            "matches_played": total,
        }
    except requests.RequestException as e:
        logger.error(f"OpenDota API error: {e}")
        return None
