from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from backend.database import Base

class LeaderboardCache(Base):
    __tablename__ = "leaderboard_cache"

    game: Mapped[str] = mapped_column(String(32), primary_key=True)
    season: Mapped[str] = mapped_column(String(16), default='current')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    json_payload: Mapped[list | dict | None] = mapped_column(JSONB)
