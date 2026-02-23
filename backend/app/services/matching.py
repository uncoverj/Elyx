from datetime import datetime, timedelta

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Like, Match, Profile, Skip, Stats, TrustVote, User

RANK_ORDER = {
    "iron": 1,
    "bronze": 2,
    "silver": 3,
    "gold": 4,
    "platinum": 5,
    "diamond": 6,
    "ascendant": 7,
    "immortal": 8,
    "radiant": 9,
}


def normalize_rank(rank_name: str | None) -> int | None:
    if not rank_name:
        return None
    return RANK_ORDER.get(rank_name.lower())


def rank_similarity(a: str | None, b: str | None) -> float:
    left = normalize_rank(a)
    right = normalize_rank(b)
    if left is None or right is None:
        return 0.25
    diff = abs(left - right)
    if diff >= 6:
        return 0.0
    return max(0.0, 1 - diff / 6)


def tag_overlap(tags_a: list[str], tags_b: list[str]) -> float:
    if not tags_a or not tags_b:
        return 0.0
    s_a, s_b = set(tags_a), set(tags_b)
    return len(s_a.intersection(s_b)) / max(len(s_a), len(s_b))


async def trust_map(db: AsyncSession) -> dict[int, tuple[int, int, float]]:
    result = await db.execute(
        select(
            TrustVote.to_user_id,
            func.sum(case((TrustVote.value == 1, 1), else_=0)).label("up"),
            func.sum(case((TrustVote.value == -1, 1), else_=0)).label("down"),
        ).group_by(TrustVote.to_user_id)
    )
    mapping: dict[int, tuple[int, int, float]] = {}
    for to_user_id, up, down in result.all():
        up = int(up or 0)
        down = int(down or 0)
        total = up + down
        score = up / total if total else 0.5
        mapping[int(to_user_id)] = (up, down, score)
    return mapping


async def next_candidate(db: AsyncSession, user_id: int) -> Profile | None:
    me_profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not me_profile:
        return None

    me_stats = (await db.execute(select(Stats).where(Stats.user_id == user_id))).scalar_one_or_none()

    excluded_subquery = (
        select(Like.to_user_id.label("uid")).where(Like.from_user_id == user_id)
        .union(select(Skip.to_user_id.label("uid")).where(Skip.from_user_id == user_id))
        .union(select(Match.user_a.label("uid")).where(Match.user_b == user_id))
        .union(select(Match.user_b.label("uid")).where(Match.user_a == user_id))
    ).subquery()

    base_query = (
        select(Profile, User.last_active_at)
        .join(User, User.id == Profile.user_id)
        .where(
            and_(
                Profile.user_id != user_id,
                Profile.game_id == me_profile.game_id,
                ~Profile.user_id.in_(select(excluded_subquery.c.uid)),
                User.is_banned.is_(False),
            )
        )
        .limit(100)
    )
    candidates = (await db.execute(base_query)).all()
    if not candidates:
        return None

    trust_scores = await trust_map(db)
    scored: list[tuple[float, Profile]] = []

    now = datetime.utcnow()
    for profile, last_active_at in candidates:
        target_stats = (await db.execute(select(Stats).where(Stats.user_id == profile.user_id))).scalar_one_or_none()
        rank_sim = rank_similarity(me_stats.rank_name if me_stats else None, target_stats.rank_name if target_stats else None)
        _, _, trust = trust_scores.get(profile.user_id, (0, 0, 0.5))
        overlap = tag_overlap(me_profile.tags or [], profile.tags or [])
        recency = 1.0 if last_active_at and last_active_at > now - timedelta(days=2) else 0.3
        score = 0.45 * rank_sim + 0.35 * trust + 0.15 * overlap + 0.05 * recency
        scored.append((score, profile))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]
