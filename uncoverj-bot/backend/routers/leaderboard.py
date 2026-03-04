from fastapi import APIRouter
from sqlalchemy import select
from backend.database import async_session_maker
from backend.models.leaderboard import LeaderboardCache

router = APIRouter()


@router.get("/leaderboard/{game}")
async def get_leaderboard(game: str, page: int = 1, per_page: int = 20):
    """
    GET /api/leaderboard/{game}?page=1&per_page=20
    Возвращает топ игроков из кэшированного лидерборда.
    """
    async with async_session_maker() as session:
        lb = await session.get(LeaderboardCache, game)
        if not lb or not lb.json_payload:
            return {"game": game, "players": [], "total": 0, "page": page}

        players = lb.json_payload
        total = len(players)

        # Пагинация
        start = (page - 1) * per_page
        end = start + per_page
        page_players = players[start:end]

        return {
            "game": game,
            "total": total,
            "page": page,
            "per_page": per_page,
            "players": page_players,
            "updated_at": lb.updated_at.isoformat() if lb.updated_at else None
        }
