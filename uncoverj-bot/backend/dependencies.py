from backend.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session() -> AsyncSession:
    """Dependency для FastAPI: async database session"""
    async with async_session_maker() as session:
        yield session
