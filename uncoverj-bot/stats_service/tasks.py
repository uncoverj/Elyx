"""
Celery-задачи для обновления статистики и лидерборда.
Все задачи — синхронные (Celery worker), поэтому используем requests, а не aiohttp.
Для работы с БД используем синхронную обёртку asyncio.run().
"""
import asyncio
import logging
from datetime import datetime

from stats_service.worker import celery_app
from stats_service.riot_api import fetch_valorant_mmr, fetch_valorant_stats
from stats_service.steam_api import fetch_cs2_stats, fetch_dota2_stats
from stats_service.normalizer import (
    normalize_valorant, normalize_cs2, normalize_dota2,
    get_rank_text_from_tier_id, get_dota2_rank_text
)

logger = logging.getLogger(__name__)


async def _update_single_user(user_id: int, game: str, game_id: str):
    """Асинхронная логика обновления одного пользователя"""
    from backend.database import async_session_maker
    from backend.models.stats import StatsSnapshot
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    result_data = {
        "rank_text": None,
        "rank_tier_id": None,
        "rank_points": None,
        "unified_score": 0,
        "kd_ratio": None,
        "winrate": None,
        "matches_played": 0,
        "source_status": "ok",
    }

    if game == "valorant":
        # Парсим Riot ID: name#tag
        parts = game_id.split("#", 1)
        if len(parts) != 2:
            result_data["source_status"] = "error"
        else:
            name, tag = parts
            mmr_data = fetch_valorant_mmr(name, tag)
            if mmr_data:
                tier_id = mmr_data.get("currenttier", 0)
                rr = mmr_data.get("ranking_in_tier", 0)
                result_data["rank_text"] = mmr_data.get("currenttierpatched", "Unranked")
                result_data["rank_tier_id"] = tier_id
                result_data["rank_points"] = rr
                result_data["unified_score"] = normalize_valorant(tier_id, rr)
            else:
                result_data["source_status"] = "notfound"

            match_stats = fetch_valorant_stats(name, tag)
            if match_stats:
                result_data["kd_ratio"] = match_stats["kd_ratio"]
                result_data["winrate"] = match_stats["winrate"]
                result_data["matches_played"] = match_stats["matches_played"]

    elif game == "cs2":
        stats = fetch_cs2_stats(game_id)
        if stats:
            if stats.get("source_status") == "private":
                result_data["source_status"] = "private"
            else:
                result_data["kd_ratio"] = stats.get("kd_ratio")
                result_data["winrate"] = stats.get("winrate")
                result_data["matches_played"] = stats.get("matches_played", 0)
                result_data["unified_score"] = normalize_cs2(
                    stats.get("kd_ratio"), stats.get("winrate")
                )
                result_data["rank_text"] = "CS2"  # CS2 не выдаёт ранг через API
        else:
            result_data["source_status"] = "notfound"

    elif game == "dota2":
        stats = fetch_dota2_stats(game_id)
        if stats:
            mmr = stats.get("mmr", 0)
            rank_tier = stats.get("rank_tier")
            result_data["rank_text"] = get_dota2_rank_text(rank_tier)
            result_data["rank_tier_id"] = rank_tier
            result_data["rank_points"] = mmr
            result_data["unified_score"] = normalize_dota2(mmr)
            result_data["kd_ratio"] = stats.get("kd_ratio")
            result_data["winrate"] = stats.get("winrate")
            result_data["matches_played"] = stats.get("matches_played", 0)
        else:
            result_data["source_status"] = "notfound"

    elif game == "lol":
        # TODO: Реализовать LoL
        result_data["source_status"] = "error"

    # Сохраняем в БД (UPSERT)
    async with async_session_maker() as session:
        stmt = pg_insert(StatsSnapshot).values(
            user_id=user_id,
            game=game,
            rank_text=result_data["rank_text"],
            rank_tier_id=result_data["rank_tier_id"],
            rank_points=result_data["rank_points"],
            unified_score=result_data["unified_score"],
            kd_ratio=result_data["kd_ratio"],
            winrate=result_data["winrate"],
            matches_played=result_data["matches_played"],
            source_status=result_data["source_status"],
            updated_at=datetime.utcnow(),
        ).on_conflict_do_update(
            constraint="uq_stats_snapshot_user_game",
            set_={
                "rank_text": result_data["rank_text"],
                "rank_tier_id": result_data["rank_tier_id"],
                "rank_points": result_data["rank_points"],
                "unified_score": result_data["unified_score"],
                "kd_ratio": result_data["kd_ratio"],
                "winrate": result_data["winrate"],
                "matches_played": result_data["matches_played"],
                "source_status": result_data["source_status"],
                "updated_at": datetime.utcnow(),
            }
        )
        await session.execute(stmt)
        await session.commit()

    logger.info(f"Updated stats for user_id={user_id}, game={game}, status={result_data['source_status']}")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def update_user_stats(self, user_id: int, game: str, game_id: str):
    """
    Celery task: обновить статистику одного пользователя.
    Вызывается при привязке аккаунта или по расписанию.
    Retry: 3 попытки с задержкой 60 секунд.
    """
    try:
        asyncio.run(_update_single_user(user_id, game, game_id))
    except Exception as exc:
        logger.error(f"Error updating stats for user_id={user_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def update_all_users_stats():
    """
    Celery task: обновить статистику ВСЕХ пользователей с привязанными аккаунтами.
    Запускается по расписанию (Celery Beat, каждые 6 часов).
    """
    async def _run():
        from backend.database import async_session_maker
        from backend.models.accounts_link import AccountLink
        from sqlalchemy import select

        async with async_session_maker() as session:
            stmt = select(AccountLink)
            result = await session.execute(stmt)
            accounts = result.scalars().all()

        for acc in accounts:
            # Ставим задачу в очередь для каждого аккаунта (параллельно через Celery)
            update_user_stats.delay(acc.user_id, acc.game, acc.game_id)

        logger.info(f"Scheduled stats update for {len(accounts)} accounts")

    asyncio.run(_run())


@celery_app.task
def rebuild_leaderboard_cache():
    """
    Celery task: пересборка кэша лидерборда.
    Запускается каждые 15 минут через Celery Beat.
    """
    async def _run():
        from backend.database import async_session_maker
        from backend.models.stats import StatsSnapshot
        from backend.models.profile import Profile
        from backend.models.leaderboard import LeaderboardCache
        from sqlalchemy import select, and_
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        import json

        games = ["valorant", "cs2", "dota2", "lol"]

        async with async_session_maker() as session:
            for game in games:
                stmt = select(
                    StatsSnapshot, Profile
                ).join(
                    Profile, and_(
                        Profile.user_id == StatsSnapshot.user_id,
                        Profile.game_primary == game
                    )
                ).where(
                    and_(
                        StatsSnapshot.game == game,
                        StatsSnapshot.source_status == "ok",
                        StatsSnapshot.unified_score != None
                    )
                ).order_by(
                    StatsSnapshot.unified_score.desc()
                ).limit(1000)

                result = await session.execute(stmt)
                rows = result.all()

                leaderboard = []
                for i, (stat, prof) in enumerate(rows, 1):
                    leaderboard.append({
                        "rank": i,
                        "nickname": prof.nickname,
                        "score": stat.unified_score,
                        "rank_text": stat.rank_text,
                        "kd_ratio": stat.kd_ratio,
                        "winrate": stat.winrate,
                    })

                # UPSERT лидерборда
                lb_stmt = pg_insert(LeaderboardCache).values(
                    game=game,
                    json_payload=leaderboard,
                    updated_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["game"],
                    set_={
                        "json_payload": leaderboard,
                        "updated_at": datetime.utcnow()
                    }
                )
                await session.execute(lb_stmt)

            await session.commit()

        logger.info(f"Leaderboard cache rebuilt for {len(games)} games")

    asyncio.run(_run())
