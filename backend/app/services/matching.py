"""Matching service — finds the best next candidate for a user.

Scoring weights (dating-oriented):
  0.40 * rank_similarity (unified_score based)
  0.20 * weighted_trust
  0.15 * mood_boost (same mood in last 24h)
  0.10 * tag_overlap
  0.10 * activity_recency
  0.05 * premium_boost
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Like, Match, Profile, Skip, Stats, User
from app.services.trust import compute_weighted_trust

# Max unified_score gap for rank_similarity to be non-zero
MAX_SCORE_GAP = 4000


def rank_similarity_unified(my_score: int, their_score: int) -> float:
    """Compare two unified scores (0-10000). Returns 0.0-1.0."""
    if my_score == 0 or their_score == 0:
        return 0.25  # unknown rank — neutral
    gap = abs(my_score - their_score)
    if gap >= MAX_SCORE_GAP:
        return 0.0
    return max(0.0, 1.0 - gap / MAX_SCORE_GAP)


def tag_overlap(tags_a: list[str], tags_b: list[str]) -> float:
    if not tags_a or not tags_b:
        return 0.0
    s_a, s_b = set(tags_a), set(tags_b)
    return len(s_a & s_b) / max(len(s_a), len(s_b))


def activity_score(last_active_at: datetime | None) -> float:
    """Score based on how recently the user was active."""
    if not last_active_at:
        return 0.1
    now = datetime.now(timezone.utc)
    la = last_active_at if last_active_at.tzinfo else last_active_at.replace(tzinfo=timezone.utc)
    hours_ago = (now - la).total_seconds() / 3600
    if hours_ago < 1:
        return 1.0
    elif hours_ago < 6:
        return 0.9
    elif hours_ago < 24:
        return 0.7
    elif hours_ago < 72:
        return 0.4
    return 0.15


def mood_boost_score(my_mood: str | None, their_mood: str | None, their_mood_at: datetime | None) -> float:
    """Boost if both users have the same mood set within last 24h."""
    if not my_mood or not their_mood:
        return 0.0
    if my_mood != their_mood:
        return 0.1  # slight boost for having any mood set
    # Same mood — check recency
    if their_mood_at:
        now = datetime.now(timezone.utc)
        mood_at = their_mood_at if their_mood_at.tzinfo else their_mood_at.replace(tzinfo=timezone.utc)
        hours_ago = (now - mood_at).total_seconds() / 3600
        if hours_ago > 24:
            return 0.2  # stale mood, small boost
    return 1.0  # same mood, recent


async def next_candidate(db: AsyncSession, user_id: int) -> Profile | None:
    me_profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not me_profile:
        return None

    me_stats = (await db.execute(select(Stats).where(Stats.user_id == user_id))).scalar_one_or_none()
    my_unified = me_stats.unified_score if me_stats else 0

    excluded_subquery = (
        select(Like.to_user_id.label("uid")).where(Like.from_user_id == user_id)
        .union(select(Skip.to_user_id.label("uid")).where(Skip.from_user_id == user_id))
        .union(select(Match.user_a.label("uid")).where(Match.user_b == user_id))
        .union(select(Match.user_b.label("uid")).where(Match.user_a == user_id))
    ).subquery()

    base_query = (
        select(Profile, User.last_active_at, User.is_premium)
        .join(User, User.id == Profile.user_id)
        .where(
            and_(
                Profile.user_id != user_id,
                Profile.game_id == me_profile.game_id,
                ~Profile.user_id.in_(select(excluded_subquery.c.uid)),
                User.is_banned.is_(False),
            )
        )
        .limit(150)
    )
    candidates = (await db.execute(base_query)).all()
    if not candidates:
        return None

    scored: list[tuple[float, Profile]] = []

    for profile, last_active_at, is_premium in candidates:
        target_stats = (await db.execute(select(Stats).where(Stats.user_id == profile.user_id))).scalar_one_or_none()
        their_unified = target_stats.unified_score if target_stats else 0

        rank_sim = rank_similarity_unified(my_unified, their_unified)
        _, _, trust = await compute_weighted_trust(db, profile.user_id)
        overlap = tag_overlap(me_profile.tags or [], profile.tags or [])
        recency = activity_score(last_active_at)
        premium_b = 1.0 if is_premium else 0.0
        mood_b = mood_boost_score(me_profile.mood_status, profile.mood_status, profile.mood_updated_at)

        score = (
            0.40 * rank_sim
            + 0.20 * trust
            + 0.15 * mood_b
            + 0.10 * overlap
            + 0.10 * recency
            + 0.05 * premium_b
        )
        scored.append((score, profile))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]

