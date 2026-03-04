from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Any
from .base import Base

class LeaderboardCache(Base):
    __tablename__ = "leaderboard_cache"

    game: Mapped[str] = mapped_column(String(32), primary_key=True)
    season: Mapped[str] = mapped_column(String(16), default="current", server_default="current")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now())
    json_payload: Mapped[Any] = mapped_column(JSONB, nullable=True)  # top 1000 players
