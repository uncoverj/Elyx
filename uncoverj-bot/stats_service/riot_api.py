"""
Клиент Henrik Dev API для получения статистики Valorant.
Henrik API (https://docs.henrikdev.xyz/) — бесплатный прокси для Riot API.
Также используется для LoL.
"""
import requests
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

HENRIK_BASE_URL = "https://api.henrikdev.xyz"


def fetch_valorant_account(name: str, tag: str) -> dict | None:
    """
    Получить аккаунт Valorant по Riot ID (name#tag).
    Возвращает dict с puuid и прочими данными, либо None при ошибке.
    """
    url = f"{HENRIK_BASE_URL}/valorant/v1/account/{name}/{tag}"
    headers = {}
    if settings.riot_api_key:
        headers["Authorization"] = settings.riot_api_key.get_secret_value()

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            return data
        elif resp.status_code == 404:
            logger.warning(f"Valorant account not found: {name}#{tag}")
            return None
        else:
            logger.error(f"Henrik API error {resp.status_code}: {resp.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Henrik API connection error: {e}")
        return None


def fetch_valorant_mmr(name: str, tag: str, region: str = "eu") -> dict | None:
    """
    Получить MMR / ранг Valorant.
    Возвращает: {
        'currenttierpatched': 'Platinum 3',
        'currenttier': 18,       # числовой ID (0=Iron1 ... 27=Radiant)
        'ranking_in_tier': 45,   # RR (0-100)
        'elo': 1845,             # общий ELO
    }
    """
    url = f"{HENRIK_BASE_URL}/valorant/v1/mmr/{region}/{name}/{tag}"
    headers = {}
    if settings.riot_api_key:
        headers["Authorization"] = settings.riot_api_key.get_secret_value()

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", {})
        elif resp.status_code == 404:
            logger.warning(f"Valorant MMR not found: {name}#{tag}")
            return None
        else:
            logger.error(f"Henrik MMR API error {resp.status_code}: {resp.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Henrik MMR API connection error: {e}")
        return None


def fetch_valorant_stats(name: str, tag: str, region: str = "eu") -> dict | None:
    """
    Получить матч-статистику (K/D, WR, матчи) через Henrik v3 matches или v1 lifetime.
    Возвращает dict с kd_ratio, winrate, matches_played.
    """
    url = f"{HENRIK_BASE_URL}/valorant/v1/lifetime/matches/{region}/{name}/{tag}?size=20"
    headers = {}
    if settings.riot_api_key:
        headers["Authorization"] = settings.riot_api_key.get_secret_value()

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None

        matches = resp.json().get("data", [])
        if not matches:
            return None

        total_kills = 0
        total_deaths = 0
        wins = 0
        total = len(matches)

        for m in matches:
            stats = m.get("stats", {})
            total_kills += stats.get("kills", 0)
            total_deaths += stats.get("deaths", 1)  # Избегаем деления на 0

            # Определяем победу
            team = stats.get("team", "").lower()
            teams = m.get("teams", {})
            if team in teams and teams[team].get("has_won", False):
                wins += 1

        kd = round(total_kills / max(total_deaths, 1), 2)
        wr = round(wins / max(total, 1), 3)

        return {
            "kd_ratio": kd,
            "winrate": wr,
            "matches_played": total,
        }

    except requests.RequestException as e:
        logger.error(f"Henrik match stats error: {e}")
        return None


def fetch_lol_stats(name: str, tag: str) -> dict | None:
    """
    Заглушка для LoL через Riot API / Henrik.
    TODO: Реализовать через Riot API v5 с собственным ключом.
    """
    logger.info(f"LoL stats fetch not yet implemented for {name}#{tag}")
    return None
