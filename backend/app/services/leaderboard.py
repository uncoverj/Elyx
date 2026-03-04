"""Leaderboard service — builds and caches per-game leaderboards.

Reads from Stats + Profile tables, computes positions, writes to
LeaderboardEntry for fast reads. Designed to run on a schedule or
triggered after stats refresh.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, LeaderboardEntry, Profile, Stats, User

logger = logging.getLogger(__name__)


async def rebuild_leaderboard(db: AsyncSession, game_id: int) -> int:
    """Rebuild the leaderboard for a single game.

    Returns the number of entries written.
    """
    rows = (
        await db.execute(
            select(Profile, Stats, User)
            .join(Stats, Stats.user_id == Profile.user_id)
            .join(User, User.id == Profile.user_id)
            .where(
                and_(
                    Profile.game_id == game_id,
                    Stats.unified_score > 0,
                    User.is_banned.is_(False),
                )
            )
            .order_by(Stats.unified_score.desc())
        )
    ).all()

    if not rows:
        return 0

    # Delete old entries for this game
    await db.execute(delete(LeaderboardEntry).where(LeaderboardEntry.game_id == game_id))

    now = datetime.now(timezone.utc)
    entries: list[LeaderboardEntry] = []
    for position, (profile, stats, user) in enumerate(rows, start=1):
        entries.append(
            LeaderboardEntry(
                game_id=game_id,
                user_id=profile.user_id,
                nickname=profile.nickname,
                rank_name=stats.rank_name,
                rank_points=stats.rank_points,
                unified_score=stats.unified_score,
                kd=stats.kd,
                winrate=stats.winrate,
                position=position,
                updated_at=now,
            )
        )

    db.add_all(entries)
    await db.commit()
    logger.info("Rebuilt leaderboard for game_id=%s: %d entries", game_id, len(entries))
    return len(entries)


async def rebuild_all_leaderboards(db: AsyncSession) -> dict[str, int]:
    """Rebuild leaderboards for all active games. Returns {game_name: count}."""
    games = (await db.execute(select(Game).where(Game.is_active.is_(True)))).scalars().all()
    results: dict[str, int] = {}
    for game in games:
        count = await rebuild_leaderboard(db, game.id)
        results[game.name] = count
    return results


async def get_leaderboard(
    db: AsyncSession,
    game_id: int,
    offset: int = 0,
    limit: int = 50,
) -> list[dict]:
    """Get cached leaderboard entries for a game with pagination."""
    rows = (
        await db.execute(
            select(LeaderboardEntry)
            .where(LeaderboardEntry.game_id == game_id)
            .order_by(LeaderboardEntry.position.asc())
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    return [
        {
            "position": entry.position,
            "user_id": entry.user_id,
            "nickname": entry.nickname,
            "rank_name": entry.rank_name,
            "rank_points": entry.rank_points,
            "unified_score": entry.unified_score,
            "kd": entry.kd,
            "winrate": entry.winrate,
        }
        for entry in rows
    ]


async def get_user_position(db: AsyncSession, game_id: int, user_id: int) -> dict | None:
    """Get a specific user's leaderboard position."""
    entry = (
        await db.execute(
            select(LeaderboardEntry).where(
                and_(LeaderboardEntry.game_id == game_id, LeaderboardEntry.user_id == user_id)
            )
        )
    ).scalar_one_or_none()

    if not entry:
        return None

    total = (
        await db.execute(
            select(LeaderboardEntry.id).where(LeaderboardEntry.game_id == game_id)
        )
    ).all()

    return {
        "position": entry.position,
        "total": len(total),
        "nickname": entry.nickname,
        "rank_name": entry.rank_name,
        "unified_score": entry.unified_score,
        "kd": entry.kd,
        "winrate": entry.winrate,
    }
