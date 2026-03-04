from sqlalchemy import select, and_, not_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from backend.models.user import User
from backend.models.profile import Profile
from backend.models.stats import StatsSnapshot
from backend.models.swipe import Swipe

async def get_next_profile(session: AsyncSession, user_id: int, game: str, user_score: int | None = None) -> tuple[Profile | None, StatsSnapshot | None, User | None]:
    """
    Алгоритм подбора анкет
    1. Только выбранная игра
    2. Исключить уже лайкнутых / скипнутых
    3. Ранговый диапазон: unified_score ± 500
    4. Активность: last_seen не старше 30 дней
    5. Сортировка: ближе по unified_score, потом по last_seen DESC
    """
    # 1. Получаем список ID, которые юзер уже свайпнул в этой игре
    swiped_query = select(Swipe.to_user_id).where(
        and_(
            Swipe.from_user_id == user_id,
            Swipe.game == game
        )
    )
    swiped_result = await session.execute(swiped_query)
    swiped_ids = swiped_result.scalars().all()
    
    # 2. Формируем основной запрос
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    stmt = select(Profile, StatsSnapshot, User).join(
        User, Profile.user_id == User.id
    ).outerjoin(
        StatsSnapshot, and_(StatsSnapshot.user_id == User.id, StatsSnapshot.game == game)
    ).where(
        and_(
            Profile.user_id != user_id,           # Не себя
            Profile.game_primary == game,         # Нужная игра
            Profile.is_visible == True,           # Видимый профиль
            User.is_banned == False,              # Не в бане
            User.last_seen >= thirty_days_ago,    # Активен последние 30 дней
            not_(Profile.user_id.in_(swiped_ids)) # Ещё не свайпнут
        )
    )
    
    # 3. Фильтр по unified_score, если он есть у юзера
    if user_score is not None:
        stmt = stmt.where(
            or_(
                StatsSnapshot.unified_score == None,
                and_(
                    StatsSnapshot.unified_score >= user_score - 500,
                    StatsSnapshot.unified_score <= user_score + 500
                )
            )
        )
        # Сортировка: ближе по score, потом по активности
        # Для null-score считаем разницу 0 (или можно убрать в конец)
        stmt = stmt.order_by(
            func.abs(func.coalesce(StatsSnapshot.unified_score, user_score) - user_score),
            User.last_seen.desc()
        )
    else:
        # Если у юзера нет score, просто сортируем по активности
        stmt = stmt.order_by(User.last_seen.desc())
        
    stmt = stmt.limit(1)
    
    result = await session.execute(stmt)
    row = result.first()
    
    if row:
        return row[0], row[1], row[2]  # Profile, StatsSnapshot, User
    return None, None, None
