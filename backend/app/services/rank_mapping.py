"""Unified rank scoring: maps game-specific ranks to a 0–10000 universal scale.

Each game has its own rank ladder. We map every tier to a base score,
then add intra-rank points (RR, LP, MMR remainder) for precision.

The unified_score is what powers the leaderboard and rank-based matching.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Valorant: Iron 1 → Radiant  (9 tiers × 3 divisions = 27 steps + Radiant)
# RR range per division: 0-99
# ---------------------------------------------------------------------------
_VALORANT_TIERS: dict[str, int] = {}

_VAL_NAMES = [
    "iron 1", "iron 2", "iron 3",
    "bronze 1", "bronze 2", "bronze 3",
    "silver 1", "silver 2", "silver 3",
    "gold 1", "gold 2", "gold 3",
    "platinum 1", "platinum 2", "platinum 3",
    "diamond 1", "diamond 2", "diamond 3",
    "ascendant 1", "ascendant 2", "ascendant 3",
    "immortal 1", "immortal 2", "immortal 3",
    "radiant",
]

for _i, _name in enumerate(_VAL_NAMES):
    _VALORANT_TIERS[_name] = 500 + _i * 330  # ~500 .. ~8840

# Aliases without number (e.g. "Platinum 3" from API may be "platinum 3")
# Already covered by lowering.

# ---------------------------------------------------------------------------
# CS2: Silver I → Global Elite  (18 ranks)
# No sub-rank points in official system, so just base score.
# ---------------------------------------------------------------------------
_CS2_RANKS = [
    "silver i", "silver ii", "silver iii", "silver iv",
    "silver elite", "silver elite master",
    "gold nova i", "gold nova ii", "gold nova iii", "gold nova master",
    "master guardian i", "master guardian ii", "master guardian elite",
    "distinguished master guardian",
    "legendary eagle", "legendary eagle master",
    "supreme master first class",
    "the global elite",
]
_CS2_TIERS: dict[str, int] = {}
for _i, _name in enumerate(_CS2_RANKS):
    _CS2_TIERS[_name] = 500 + _i * 500  # ~500 .. ~9000

# Numbered alias support (CS rating tiers)
_CS2_TIERS.update({
    "silver 1": _CS2_TIERS["silver i"],
    "silver 2": _CS2_TIERS["silver ii"],
    "silver 3": _CS2_TIERS["silver iii"],
    "silver 4": _CS2_TIERS["silver iv"],
})

# ---------------------------------------------------------------------------
# Dota 2: Herald → Immortal (8 tiers × ~5 stars, + Immortal top)
# MMR roughly: Herald 0-769, Guardian 770-1539, ... Immortal 5420+
# We use MMR directly when available; rank_name as fallback.
# ---------------------------------------------------------------------------
_DOTA_TIERS: dict[str, int] = {
    "herald": 700,
    "guardian": 1500,
    "crusader": 2300,
    "archon": 3100,
    "legend": 4000,
    "ancient": 5000,
    "divine": 6200,
    "immortal": 7800,
}

# With stars
for _base_name, _base_score in list(_DOTA_TIERS.items()):
    for _star in range(1, 6):
        _DOTA_TIERS[f"{_base_name} {_star}"] = _base_score + (_star - 1) * 150

# ---------------------------------------------------------------------------
# League of Legends: Iron → Challenger (10 tiers × 4 divisions + master+)
# LP: 0-100 per division
# ---------------------------------------------------------------------------
_LOL_TIER_BASES = {
    "iron": 500,
    "bronze": 1200,
    "silver": 1900,
    "gold": 2600,
    "platinum": 3300,
    "emerald": 4000,
    "diamond": 4700,
    "master": 5800,
    "grandmaster": 7200,
    "challenger": 8600,
}
_LOL_TIERS: dict[str, int] = {}
for _tier, _base in _LOL_TIER_BASES.items():
    _LOL_TIERS[_tier] = _base
    # LoL divisions: IV=1, III=2, II=3, I=4 (IV is lowest)
    for _div_num, _div_name in [(4, "iv"), (3, "iii"), (2, "ii"), (1, "i")]:
        _LOL_TIERS[f"{_tier} {_div_name}"] = _base + (_div_num - 1) * 170

# ---------------------------------------------------------------------------
# Apex Legends: Rookie → Apex Predator
# ---------------------------------------------------------------------------
_APEX_TIERS: dict[str, int] = {
    "rookie": 500,
    "bronze": 1200,
    "silver": 2000,
    "gold": 2800,
    "platinum": 3800,
    "diamond": 5000,
    "master": 6800,
    "apex predator": 8800,
}
for _base_name, _base_score in list(_APEX_TIERS.items()):
    for _div in range(1, 5):
        _APEX_TIERS[f"{_base_name} {_div}"] = _base_score + (_div - 1) * 180

# ---------------------------------------------------------------------------
# Overwatch 2: Bronze → Champion (7 tiers × 5 divisions)
# ---------------------------------------------------------------------------
_OW2_TIERS: dict[str, int] = {
    "bronze": 500,
    "silver": 1400,
    "gold": 2300,
    "platinum": 3200,
    "diamond": 4200,
    "master": 5400,
    "grandmaster": 6800,
    "champion": 8500,
}
for _base_name, _base_score in list(_OW2_TIERS.items()):
    for _div in range(1, 6):
        _OW2_TIERS[f"{_base_name} {_div}"] = _base_score + (_div - 1) * 170


# ========================== PUBLIC API ==========================

GAME_RANK_MAPS: dict[str, dict[str, int]] = {
    "valorant": _VALORANT_TIERS,
    "cs2": _CS2_TIERS,
    "dota 2": _DOTA_TIERS,
    "league of legends": _LOL_TIERS,
    "apex legends": _APEX_TIERS,
    "overwatch 2": _OW2_TIERS,
}

# Tier IDs for fast integer sorting (rank_tier_id in DB)
GAME_TIER_IDS: dict[str, dict[str, int]] = {}
for _game, _mapping in GAME_RANK_MAPS.items():
    sorted_ranks = sorted(_mapping.items(), key=lambda x: x[1])
    GAME_TIER_IDS[_game] = {name: idx for idx, (name, _) in enumerate(sorted_ranks)}


def compute_unified_score(
    game_name: str,
    rank_name: str | None,
    rank_points: int | None = None,
) -> int:
    """Return a unified score 0–10000 for the given game rank.

    rank_points is RR/LP/MMR and adds precision within a tier.
    Returns 0 if rank is unknown.
    """
    if not rank_name:
        return 0

    game_key = game_name.lower()
    rank_key = rank_name.strip().lower()
    mapping = GAME_RANK_MAPS.get(game_key)
    if not mapping:
        return 0

    # Dota 2 special case: if we have raw MMR, use it directly (scaled)
    if game_key == "dota 2" and rank_points and rank_points > 100:
        # MMR ranges roughly 0-12000; map to 500-9500
        return min(9500, max(500, int(rank_points * 0.75 + 500)))

    base = mapping.get(rank_key)
    if base is None:
        # Try fuzzy: strip trailing digits/stars
        for known in mapping:
            if rank_key.startswith(known) or known.startswith(rank_key):
                base = mapping[known]
                break
    if base is None:
        return 0

    # Add intra-rank precision from rank_points (RR/LP: typically 0-100)
    bonus = 0
    if rank_points is not None and rank_points >= 0:
        if game_key in ("valorant", "league of legends"):
            bonus = min(rank_points, 100) * 3  # up to +300
        else:
            bonus = min(rank_points, 100) * 2  # up to +200

    return min(10000, base + bonus)


def get_rank_tier_id(game_name: str, rank_name: str | None) -> int:
    """Return a numeric tier ID for DB sorting. Higher = better rank."""
    if not rank_name:
        return 0
    game_key = game_name.lower()
    rank_key = rank_name.strip().lower()
    tier_map = GAME_TIER_IDS.get(game_key, {})
    tid = tier_map.get(rank_key)
    if tid is not None:
        return tid
    # Fuzzy match
    for known, known_id in tier_map.items():
        if rank_key.startswith(known) or known.startswith(rank_key):
            return known_id
    return 0
