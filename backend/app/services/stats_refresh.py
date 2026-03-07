"""Unified stats refresh service for the currently supported games."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExternalAccount, Game, Profile, Stats
from app.services.rank_mapping import compute_unified_score, get_rank_tier_id

logger = logging.getLogger(__name__)

GAME_PROVIDER_MAP = {
    "valorant": "riot",
    "cs2": "faceit",
}

PROVIDER_LABELS = {
    "riot": "Riot ID (Name#Tag)",
    "faceit": "FACEIT nickname",
}


async def _find_account(db: AsyncSession, user_id: int, provider: str) -> ExternalAccount | None:
    return (
        await db.execute(
            select(ExternalAccount).where(
                ExternalAccount.user_id == user_id,
                ExternalAccount.provider == provider,
            )
        )
    ).scalar_one_or_none()


async def refresh_user_stats(db: AsyncSession, user_id: int) -> dict:
    """Pull live stats from external APIs and update the Stats row."""
    profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not profile:
        return {"ok": False, "error": "no_profile"}

    game = (await db.execute(select(Game).where(Game.id == profile.game_id))).scalar_one_or_none()
    if not game:
        return {"ok": False, "error": "no_game"}

    game_lower = game.name.lower()
    provider = GAME_PROVIDER_MAP.get(game_lower)
    if not provider:
        return {"ok": False, "error": "unsupported_game", "game": game.name}

    ext = await _find_account(db, user_id, provider)
    if not ext:
        return {
            "ok": False,
            "error": "no_linked_account",
            "provider": provider,
            "label": PROVIDER_LABELS.get(provider, provider),
        }

    account_ref = ext.account_ref
    fetched = None

    if game_lower == "valorant":
        from app.services.stats_valorant import fetch_valorant_stats

        fetched = await fetch_valorant_stats(account_ref)
    elif game_lower == "cs2":
        from app.services.stats_faceit import fetch_faceit_stats

        fetched = await fetch_faceit_stats(account_ref)

    if not fetched:
        if game_lower == "valorant":
            return {
                "ok": False,
                "error": "no_match_history",
                "game": game.name,
                "message": "Аккаунт найден, но в Valorant пока нет матчей для статистики.",
            }
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
    stats.unified_score = compute_unified_score(game.name, stats.rank_name, stats.rank_points)
    stats.rank_tier_id = get_rank_tier_id(game.name, stats.rank_name)

    await db.commit()
    await db.refresh(stats)

    return {
        "ok": True,
        "game": game.name,
        "provider": provider,
        "account_ref": account_ref,
        "rank": stats.rank_name,
        "rank_points": stats.rank_points,
        "unified_score": stats.unified_score,
        "kd": stats.kd,
        "winrate": stats.winrate,
        "source": stats.source,
        "verified": stats.verified,
        "updated_at": stats.updated_at.isoformat() if stats.updated_at else None,
    }
