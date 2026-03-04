"""Enhanced trust system with weighted votes.

Rules:
1. Only vote after interaction (match required — already enforced at API layer)
2. One vote per pair, with cooldown
3. Vote weight depends on account age + activity:
   - New account (< 7 days): weight 0.2
   - Normal (7-30 days): weight 0.6
   - Veteran (30+ days): weight 1.0
4. Premium does NOT give stronger vote weight (anti-pay2win)
5. Suspicion detection: many -1 votes in short time → flag
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TrustVote, User

logger = logging.getLogger(__name__)

COOLDOWN_HOURS = 24  # can change vote after this period
SUSPICION_THRESHOLD = 5  # N downvotes received within window → suspicious
SUSPICION_WINDOW_HOURS = 24


def _vote_weight(voter: User) -> float:
    """Calculate vote weight based on account age."""
    now = datetime.now(timezone.utc)
    age = now - voter.created_at.replace(tzinfo=timezone.utc) if voter.created_at.tzinfo is None else now - voter.created_at
    days = age.days

    if days < 7:
        return 0.2
    elif days < 30:
        return 0.6
    else:
        return 1.0


async def compute_weighted_trust(db: AsyncSession, target_user_id: int) -> tuple[int, int, float]:
    """Compute weighted trust score for a user.

    Returns (raw_up_count, raw_down_count, weighted_score 0.0-1.0).
    """
    votes = (
        await db.execute(
            select(TrustVote, User)
            .join(User, User.id == TrustVote.from_user_id)
            .where(TrustVote.to_user_id == target_user_id)
        )
    ).all()

    if not votes:
        return 0, 0, 0.5  # neutral default

    weighted_up = 0.0
    weighted_down = 0.0
    raw_up = 0
    raw_down = 0

    for vote, voter in votes:
        w = _vote_weight(voter)
        if vote.value == 1:
            weighted_up += w
            raw_up += 1
        else:
            weighted_down += w
            raw_down += 1

    total_weighted = weighted_up + weighted_down
    score = weighted_up / total_weighted if total_weighted > 0 else 0.5

    return raw_up, raw_down, round(score, 3)


async def check_vote_cooldown(db: AsyncSession, from_user_id: int, to_user_id: int) -> tuple[bool, int]:
    """Check if voter can change their vote (cooldown check).

    Returns (allowed, seconds_remaining).
    """
    existing = (
        await db.execute(
            select(TrustVote).where(
                and_(TrustVote.from_user_id == from_user_id, TrustVote.to_user_id == to_user_id)
            )
        )
    ).scalar_one_or_none()

    if not existing:
        return True, 0

    now = datetime.now(timezone.utc)
    vote_time = existing.created_at
    if vote_time.tzinfo is None:
        vote_time = vote_time.replace(tzinfo=timezone.utc)

    cooldown_end = vote_time + timedelta(hours=COOLDOWN_HOURS)
    if now >= cooldown_end:
        return True, 0

    remaining = int((cooldown_end - now).total_seconds())
    return False, remaining


async def check_suspicion(db: AsyncSession, target_user_id: int) -> bool:
    """Check if a user is receiving suspiciously many downvotes.

    Returns True if suspicious activity detected.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=SUSPICION_WINDOW_HOURS)

    recent_downvotes = (
        await db.execute(
            select(func.count(TrustVote.id)).where(
                and_(
                    TrustVote.to_user_id == target_user_id,
                    TrustVote.value == -1,
                    TrustVote.created_at >= window_start,
                )
            )
        )
    ).scalar_one()

    if recent_downvotes >= SUSPICION_THRESHOLD:
        logger.warning(
            "Suspicious downvote activity on user %d: %d downvotes in %d hours",
            target_user_id,
            recent_downvotes,
            SUSPICION_WINDOW_HOURS,
        )
        return True
    return False
