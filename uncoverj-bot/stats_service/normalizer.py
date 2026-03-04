"""
Нормализация рангов и расчёт unified_score (0–10000).

Алгоритм unified_score:
- Для каждой игры ранги конвертируются в единую шкалу 0–10000.
- Это позволяет сравнивать игроков разных игр в лидерборде
  и подбирать тиммейтов ±500 очков (≈ ±2 тира).

Valorant: 0 (Iron 1) → 10000 (Radiant)
  tier_id * 370 + RR * 3.7 (28 тиров: 0..27)

CS2: На основе K/D и Winrate (нет прямого MMR API)
  winrate * 5000 + kd * 2500, capped at 10000

Dota 2: MMR → score
  mmr / 1.2, capped at 10000 (12000 MMR ≈ rank #1)

LoL: LP → score (TODO)
"""
import logging

logger = logging.getLogger(__name__)


def normalize_valorant(tier_id: int | None, rr: int | None) -> int:
    """
    Конвертация ранга Valorant в unified_score.
    tier_id: 0 (Iron 1) ... 27 (Radiant)
    rr: ranking_in_tier (0-100)
    """
    if tier_id is None:
        return 0
    rr = rr or 0
    # 28 тиров, каждый тир ≈ 370 очков, RR даёт бонус внутри тира
    score = int(tier_id * 370 + rr * 3.7)
    return min(score, 10000)


def normalize_cs2(kd_ratio: float | None, winrate: float | None) -> int:
    """
    Конвертация статистики CS2 в unified_score.
    У CS2 нет публичного MMR, поэтому аппроксимируем по K/D и Winrate.
    """
    kd = kd_ratio or 0.0
    wr = winrate or 0.0
    # WR (0.0–1.0) даёт до 5000 очков, K/D (0–4+) даёт до 5000 очков
    score = int(wr * 5000 + min(kd, 2.0) * 2500)
    return min(score, 10000)


def normalize_dota2(mmr: int | None) -> int:
    """
    Конвертация MMR Dota 2 в unified_score.
    Максимальный MMR ~12000 → 10000 score.
    """
    if mmr is None or mmr <= 0:
        return 0
    score = int(mmr / 1.2)
    return min(score, 10000)


def normalize_lol(lp: int | None) -> int:
    """
    Заглушка для LoL. TODO: реализовать через тиры + LP.
    """
    if lp is None:
        return 0
    return min(lp, 10000)


def get_rank_text_from_tier_id(tier_id: int) -> str:
    """
    Конвертация числового tier_id Valorant в текстовый ранг.
    0=Iron 1, 1=Iron 2, 2=Iron 3, 3=Bronze 1 ... 24=Immortal 1, 25=Immortal 2, 26=Immortal 3, 27=Radiant
    """
    ranks = [
        "Iron 1", "Iron 2", "Iron 3",
        "Bronze 1", "Bronze 2", "Bronze 3",
        "Silver 1", "Silver 2", "Silver 3",
        "Gold 1", "Gold 2", "Gold 3",
        "Platinum 1", "Platinum 2", "Platinum 3",
        "Diamond 1", "Diamond 2", "Diamond 3",
        "Ascendant 1", "Ascendant 2", "Ascendant 3",
        "Immortal 1", "Immortal 2", "Immortal 3",
        "Radiant"
    ]
    if 0 <= tier_id < len(ranks):
        return ranks[tier_id]
    return "Unranked"


def get_dota2_rank_text(rank_tier: int | None) -> str:
    """
    Конвертация rank_tier Dota 2 в текстовый ранг.
    Первая цифра — медаль (1=Herald ... 8=Immortal), вторая — звезда (0-5).
    Например: 53 = Legend 3
    """
    if not rank_tier:
        return "Unranked"

    medals = {
        1: "Herald", 2: "Guardian", 3: "Crusader", 4: "Archon",
        5: "Legend", 6: "Ancient", 7: "Divine", 8: "Immortal"
    }
    medal = rank_tier // 10
    star = rank_tier % 10
    medal_name = medals.get(medal, "Unknown")
    if medal == 8:
        return "Immortal"
    return f"{medal_name} {star}"
