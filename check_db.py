import asyncio
from sqlalchemy import text
from backend.database import engine

async def check_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Подключение к базе данных PostgreSQL успешно установлено!")
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных:\n{e}")

if __name__ == "__main__":
    asyncio.run(check_connection())
