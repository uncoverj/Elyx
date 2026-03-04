import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import Celery
from backend.config import settings

celery_app = Celery(
    "uncoverj_stats",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["stats_service.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Celery Beat: расписание авто-обновлений
celery_app.conf.beat_schedule = {
    # Обновление статистики всех пользователей — каждые 6 часов
    "update-all-stats-every-6h": {
        "task": "stats_service.tasks.update_all_users_stats",
        "schedule": 6 * 60 * 60,  # 6 часов в секундах
    },
    # Пересборка лидерборда — каждые 15 минут
    "rebuild-leaderboard-every-15m": {
        "task": "stats_service.tasks.rebuild_leaderboard_cache",
        "schedule": 15 * 60,  # 15 минут в секундах
    },
}
