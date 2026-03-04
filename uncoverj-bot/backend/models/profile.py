from datetime import datetime
from sqlalchemy import BigInteger, String, SmallInteger, Boolean, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Any
from .base import Base

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint("age >= 14 AND age <= 60", name="check_age_range"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # 'male' | 'female' | 'hidden'
    game_primary: Mapped[str] = mapped_column(String(32), nullable=False)  # 'valorant' | 'cs2' | 'dota2' | 'lol'
    
    # JSONB тип для списков тегов
    playstyle_tags: Mapped[Any] = mapped_column(JSONB, default=[], server_default="[]")
    behavior_tags: Mapped[Any] = mapped_column(JSONB, default=[], server_default="[]")
    
    bio_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, server_default="TRUE")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="profile")
