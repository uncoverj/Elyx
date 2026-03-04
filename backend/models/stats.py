from sqlalchemy import BigInteger, SmallInteger, String, Float, Integer, DateTime, func, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base

class StatsSnapshot(Base):
    __tablename__ = "stats_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    game: Mapped[str] = mapped_column(String(32), nullable=False)
    rank_text: Mapped[str | None] = mapped_column(String(32))
    rank_tier_id: Mapped[int | None] = mapped_column(SmallInteger)
    rank_points: Mapped[int | None] = mapped_column(SmallInteger)
    unified_score: Mapped[int | None] = mapped_column(Integer)
    kd_ratio: Mapped[float | None] = mapped_column(Float)
    winrate: Mapped[float | None] = mapped_column(Float)
    matches_played: Mapped[int] = mapped_column(Integer, default=0)
    source_status: Mapped[str] = mapped_column(String(16), default='ok')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'game', name='_stats_user_game_uc'),
        Index('idx_stats_game_score', 'game', 'unified_score'), # SQLite / generic friendly, updated in migration
    )
