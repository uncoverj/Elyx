"""Unified stats refresh service.

Determines which API to call based on the user's game + linked accounts,
then writes the result into the Stats table.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExternalAccount, Game, Profile, Stats
from app.services.rank_mapping import compute_unified_score, get_rank_tier_id

logger = logging.getLogger(__name__)

GAME_PROVIDER_MAP = {
    "valorant": "riot",
    "cs2": "faceit",  # Primary: Faceit for ELO; fallback: Steam
    "dota 2": "steam",
    "league of legends": "riot",
    "apex legends": "steam",
    "overwatch 2": "blizzard",
    "fortnite": "epic",
}

# CS2 accepts multiple providers — Faceit (primary) or Steam (fallback)
CS2_PROVIDERS = ["faceit", "steam"]

PROVIDER_LABELS = {
    "riot": "Riot ID (Name#Tag)",
    "steam": "Steam ID / ссылка",
    "faceit": "Faceit никнейм",
    "blizzard": "BattleTag (Name#1234)",
    "epic": "Epic Games ник",
}


async def _find_account(db: AsyncSession, user_id: int, providers: list[str]) -> tuple[ExternalAccount | None, str | None]:
    """Find the first linked account from a list of providers."""
    for provider in providers:
        ext = (
            await db.execute(
                select(ExternalAccount).where(
                    ExternalAccount.user_id == user_id,
                    ExternalAccount.provider == provider,
                )
            )
        ).scalar_one_or_none()
        if ext:
            return ext, provider
    return None, None


async def refresh_user_stats(db: AsyncSession, user_id: int) -> dict:
    """Pull live stats from external APIs and update the Stats row.

    Returns a dict with status info for the caller.
    """
    profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not profile:
        return {"ok": False, "error": "no_profile"}

    game = (await db.execute(select(Game).where(Game.id == profile.game_id))).scalar_one_or_none()
    if not game:
        return {"ok": False, "error": "no_game"}

    game_lower = game.name.lower()

    if game_lower not in GAME_PROVIDER_MAP:
        return {"ok": False, "error": "unsupported_game", "game": game.name}

    # For CS2: check multiple providers (faceit first, then steam)
    if game_lower == "cs2":
        ext, found_provider = await _find_account(db, user_id, CS2_PROVIDERS)
    else:
        needed_provider = GAME_PROVIDER_MAP[game_lower]
        ext, found_provider = await _find_account(db, user_id, [needed_provider])

    if not ext:
        # Suggest the primary provider for the error message
        primary = GAME_PROVIDER_MAP[game_lower]
        label = PROVIDER_LABELS.get(primary, primary)
        if game_lower == "cs2":
            label = "Faceit никнейм или Steam ID"
        return {"ok": False, "error": "no_linked_account", "provider": primary, "label": label}

    account_ref = ext.account_ref
    fetched = None

    if game_lower == "valorant":
        from app.services.stats_valorant import fetch_valorant_stats
        fetched = await fetch_valorant_stats(account_ref)

    elif game_lower == "dota 2":
        from app.services.stats_dota import fetch_dota_stats
        fetched = await fetch_dota_stats(account_ref)

    elif game_lower == "cs2":
        if found_provider == "faceit":
            from app.services.stats_faceit import fetch_faceit_stats
            fetched = await fetch_faceit_stats(account_ref)
        if not fetched:
            # Try steam as fallback
            steam_ext, _ = await _find_account(db, user_id, ["steam"])
            if steam_ext:
                from app.services.stats_steam import fetch_cs2_stats
                fetched = await fetch_cs2_stats(steam_ext.account_ref)

    elif game_lower == "apex legends":
        from app.services.stats_steam import fetch_cs2_stats
        fetched = await fetch_cs2_stats(account_ref)

    elif game_lower == "league of legends":
        from app.services.stats_lol import fetch_lol_stats
        fetched = await fetch_lol_stats(account_ref)

    elif game_lower == "overwatch 2":
        from app.services.stats_ow2 import fetch_ow2_stats
        fetched = await fetch_ow2_stats(account_ref)

    elif game_lower == "fortnite":
        from app.services.stats_fortnite import fetch_fortnite_stats
        fetched = await fetch_fortnite_stats(account_ref)

    if not fetched:
        return {"ok": False, "error": "api_fetch_failed", "game": game.name}

    stats = (await db.execute(select(Stats).where(Stats.user_id == user_id))).scalar_one_or_none()
    if not stats:
        stats = Stats(user_id=user_id)
        db.add(stats)

    if fetched.kd is not None:
        stats.kd = fetched.kd
    if fetched.winrate is not None:
        stats.winrate = fetched.winrate
    if fetched.rank_name is not None:
        stats.rank_name = fetched.rank_name
    if fetched.rank_points is not None:
        stats.rank_points = fetched.rank_points
    stats.source = fetched.source
    stats.verified = fetched.verified
    stats.source_status = "ok"

    # Compute unified score and tier id for leaderboard / matching
    stats.unified_score = compute_unified_score(game.name, stats.rank_name, stats.rank_points)
    stats.rank_tier_id = get_rank_tier_id(game.name, stats.rank_name)

    await db.commit()

    return {
        "ok": True,
        "game": game.name,
        "rank": stats.rank_name,
        "rank_points": stats.rank_points,
        "unified_score": stats.unified_score,
        "kd": stats.kd,
        "winrate": stats.winrate,
        "source": stats.source,
    }
