"""
Сервис расчёта trust_score.
Вес голоса зависит от возраста аккаунта:
  - Аккаунт < 7 дней → вес 0.2
  - 7–30 дней → вес 0.5
  - > 30 дней → вес 1.0
"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.trust import TrustVote
from backend.models.user import User


def calc_vote_weight(account_created: datetime) -> float:
    """Вес голоса зависит от возраста аккаунта голосующего"""
    age = datetime.utcnow() - account_created
    if age < timedelta(days=7):
        return 0.2
    elif age < timedelta(days=30):
        return 0.5
    return 1.0


async def cast_trust_vote(session: AsyncSession, voter_id: int, target_id: int, vote: int) -> str:
    """
    Поставить голос (+1 / -1).
    Возвращает 'ok', 'already_voted' или 'no_match'.
    """
    from backend.models.match import Match
    from sqlalchemy import or_, and_
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    # 1. Проверяем, есть ли матч между ними
    match_stmt = select(Match).where(
        and_(
            or_(
                and_(Match.user1_id == voter_id, Match.user2_id == target_id),
                and_(Match.user1_id == target_id, Match.user2_id == voter_id)
            ),
            Match.status == "active"
        )
    )
    match = (await session.execute(match_stmt)).scalar_one_or_none()
    if not match:
        return "no_match"

    # 2. Считаем вес
    voter = await session.get(User, voter_id)
    weight = calc_vote_weight(voter.created_at)

    # 3. UPSERT голоса (один голос на пару voter→target)
    stmt = pg_insert(TrustVote).values(
        voter_id=voter_id,
        target_id=target_id,
        vote=vote,
        weight=weight
    ).on_conflict_do_update(
        constraint="uq_trust_votes_voter_target",
        set_={"vote": vote, "weight": weight}
    )
    await session.execute(stmt)

    # 4. Пересчитываем trust_score для target
    await recalc_trust_score(session, target_id)

    await session.commit()
    return "ok"


async def recalc_trust_score(session: AsyncSession, user_id: int):
    """
    Пересчитывает trust_score пользователя.
    Формула: base (100) + sum(vote * weight) * 5
    Ограничение: [0, 200]
    """
    stmt = select(
        func.sum(TrustVote.vote * TrustVote.weight)
    ).where(TrustVote.target_id == user_id)
    result = await session.execute(stmt)
    weighted_sum = result.scalar() or 0.0

    trust_score = max(0.0, min(200.0, 100.0 + weighted_sum * 5))

    await session.execute(
        update(User).where(User.id == user_id).values(trust_score=trust_score)
    )


async def get_trust_counts(session: AsyncSession, user_id: int) -> tuple[int, int]:
    """Получить количество позитивных и негативных голосов"""
    up_stmt = select(func.count()).where(
        TrustVote.target_id == user_id, TrustVote.vote == 1
    )
    down_stmt = select(func.count()).where(
        TrustVote.target_id == user_id, TrustVote.vote == -1
    )
    up = (await session.execute(up_stmt)).scalar() or 0
    down = (await session.execute(down_stmt)).scalar() or 0
    return up, down
