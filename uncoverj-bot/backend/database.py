import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from backend.config import settings

# Инициализация асинхронного движка SQLAlchemy 2.0 (asyncpg)
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Включи True для дебага SQL-запросов (пока выключено для прода)
    pool_size=10,
    max_overflow=20
)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def check_db_connection() -> bool:
    """Функция для проверки подключения к БД перед стартом приложения."""
    try:
        async with engine.begin() as conn:
            # Делаем простой запрос для проверки
            await conn.execute(text("SELECT 1"))
        print("✅ Успешное подключение к базе данных PostgreSQL!")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

# Тестовый запуск: вызывать из корня как `python -m backend.database`
if __name__ == "__main__":
    asyncio.run(check_db_connection())
