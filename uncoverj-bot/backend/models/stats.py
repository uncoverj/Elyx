from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, Integer, Float, DateTime, ForeignKey, UniqueConstraint, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base

class StatsSnapshot(Base):
    __tablename__ = "stats_snapshot"
    __table_args__ = (
        UniqueConstraint("user_id", "game", name="uq_stats_snapshot_user_game"),
        Index("idx_stats_game_score", "game", "unified_score", postgresql_using="btree", postgresql_ops={"unified_score": "DESC"}) # Сортировка по убыванию score
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    game: Mapped[str] = mapped_column(String(32), nullable=False)
    
    rank_text: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # 'Platinum 3', 'Immortal 1'
    rank_tier_id: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True) # 0=Iron1...27=Radiant
    rank_points: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)  # RR (0-100) or MMR or LP
    unified_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)     # 0–10000 for leaderboard
    
    kd_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    winrate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)           # 0.0–1.0
    matches_played: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    
    source_status: Mapped[str] = mapped_column(String(16), default="ok", server_default="ok") # 'ok'|'error'|'private'|'notfound'
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="stats")
