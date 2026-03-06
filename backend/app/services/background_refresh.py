"""Background stats refresh — periodic job that updates all users' stats.

Rules:
- Free users: refresh every 12-24 hours
- Premium users: refresh every 1-3 hours
- Manual refresh: premium gets instant (with cooldown), free gets 1/day

Runs as an asyncio background task inside the FastAPI lifespan.
Includes retry logic and error tracking.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Profile, Stats, User

logger = logging.getLogger(__name__)

# Refresh intervals
FREE_INTERVAL_HOURS = 18
PREMIUM_INTERVAL_HOURS = 2
MANUAL_REFRESH_COOLDOWN_FREE = timedelta(hours=12)
MANUAL_REFRESH_COOLDOWN_PREMIUM = timedelta(minutes=15)
BATCH_DELAY_SECONDS = 2.0  # delay between users to respect API rate limits
MAX_RETRIES = 2


def _naive_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt


async def _refresh_single_user(db: AsyncSession, user_id: int) -> bool:
    """Refresh a single user's stats. Returns True on success."""
    from app.services.stats_refresh import refresh_user_stats

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = await refresh_user_stats(db, user_id)
            if result.get("ok"):
                logger.debug("Refreshed stats for user %d: %s", user_id, result.get("rank"))
                return True
            else:
                error = result.get("error", "unknown")
                if error in ("no_profile", "no_linked_account", "unsupported_game", "lol_not_yet_supported"):
                    return False  # no point retrying
                logger.warning("Stats refresh failed for user %d (attempt %d): %s", user_id, attempt, error)
        except Exception as exc:
            logger.error("Stats refresh error for user %d (attempt %d): %s", user_id, attempt, exc)

        if attempt < MAX_RETRIES:
            await asyncio.sleep(1.0)

    # Mark source_status as error after all retries failed
    stats = (await db.execute(select(Stats).where(Stats.user_id == user_id))).scalar_one_or_none()
    if stats:
        stats.source_status = "error"
        await db.commit()
    return False


async def run_background_refresh_cycle(db_factory) -> dict:
    """Run one full refresh cycle for all eligible users.

    db_factory should be the SessionLocal callable.
    Returns summary dict.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    free_cutoff = now - timedelta(hours=FREE_INTERVAL_HOURS)
    premium_cutoff = now - timedelta(hours=PREMIUM_INTERVAL_HOURS)

    async with db_factory() as db:
        # Get users who have profiles (and thus might have stats to refresh)
        users_with_profiles = (
            await db.execute(
                select(User, Stats)
                .join(Profile, Profile.user_id == User.id)
                .outerjoin(Stats, Stats.user_id == User.id)
                .where(User.is_banned.is_(False))
            )
        ).all()

    refreshed = 0
    skipped = 0
    errors = 0

    for user, stats in users_with_profiles:
        last_update = _naive_utc(stats.updated_at) if stats else None
        premium_until = _naive_utc(user.premium_until)
        is_premium = user.is_premium and premium_until and premium_until > now

        # Determine if refresh is needed
        if last_update:
            cutoff = premium_cutoff if is_premium else free_cutoff
            if last_update > cutoff:
                skipped += 1
                continue

        # Refresh with per-user session to isolate failures
        async with db_factory() as db:
            success = await _refresh_single_user(db, user.id)
            if success:
                refreshed += 1
            else:
                errors += 1

        # Rate limit respect
        await asyncio.sleep(BATCH_DELAY_SECONDS)

    return {"refreshed": refreshed, "skipped": skipped, "errors": errors}


async def background_refresh_loop(db_factory, interval_minutes: int = 30) -> None:
    """Infinite loop that runs refresh cycles periodically.

    Should be started as an asyncio task during app startup.
    """
    logger.info("Background refresh loop started (interval: %d min)", interval_minutes)
    while True:
        try:
            result = await run_background_refresh_cycle(db_factory)
            logger.info(
                "Background refresh cycle done: refreshed=%d skipped=%d errors=%d",
                result["refreshed"],
                result["skipped"],
                result["errors"],
            )
        except Exception as exc:
            logger.error("Background refresh cycle crashed: %s", exc)

        await asyncio.sleep(interval_minutes * 60)


def can_manual_refresh(user: User, stats: Stats | None) -> tuple[bool, int]:
    """Check if user can trigger a manual refresh.

    Returns (allowed, seconds_until_allowed).
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    premium_until = _naive_utc(user.premium_until)
    is_premium = user.is_premium and premium_until and premium_until > now

    updated_at = _naive_utc(stats.updated_at) if stats else None
    if not updated_at:
        return True, 0

    cooldown = MANUAL_REFRESH_COOLDOWN_PREMIUM if is_premium else MANUAL_REFRESH_COOLDOWN_FREE
    next_allowed = updated_at + cooldown
    if now >= next_allowed:
        return True, 0

    remaining = int((next_allowed - now).total_seconds())
    return False, remaining
