from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        Index("idx_swipes_from", "from_user_id", "game"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(16))  # 'like' | 'skip' | 'letter'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
