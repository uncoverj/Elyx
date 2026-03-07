from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Profile, Stats, TrustVote, User
from app.schemas import ProfileOut, StatsIn


async def build_profile_out(db: AsyncSession, user_id: int) -> ProfileOut | None:
    profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not profile:
        return None

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    game = (await db.execute(select(Game).where(Game.id == profile.game_id))).scalar_one()
    stats = (await db.execute(select(Stats).where(Stats.user_id == user_id))).scalar_one_or_none()

    trust_row = (
        await db.execute(
            select(
                func.sum(case((TrustVote.value == 1, 1), else_=0)).label("up"),
                func.sum(case((TrustVote.value == -1, 1), else_=0)).label("down"),
            ).where(TrustVote.to_user_id == user_id)
        )
    ).one()

    up = int(trust_row.up or 0)
    down = int(trust_row.down or 0)
    trust_total = up + down
    trust_score = up / trust_total if trust_total else 0.5

    stats_out = None
    if stats:
        stats_out = StatsIn(
            kd=stats.kd,
            winrate=stats.winrate,
            rank_name=stats.rank_name,
            rank_points=stats.rank_points,
            unified_score=stats.unified_score,
            source=stats.source,
            source_status=stats.source_status,
            verified=stats.verified,
            updated_at=stats.updated_at,
        )

    return ProfileOut(
        user_id=profile.user_id,
        tg_id=user.tg_id,
        username=user.username,
        nickname=profile.nickname,
        gender=profile.gender,
        age=profile.age,
        game_id=profile.game_id,
        game_name=game.name,
        bio=profile.bio,
        media_type=profile.media_type,
        media_file_id=profile.media_file_id,
        roles=profile.roles or [],
        tags=profile.tags or [],
        green_flags=profile.green_flags or [],
        dealbreaker=profile.dealbreaker,
        mood_status=profile.mood_status,
        trust_up=up,
        trust_down=down,
        trust_score=trust_score,
        is_premium=user.is_premium,
        stats=stats_out,
    )
