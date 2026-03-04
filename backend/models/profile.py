from sqlalchemy import BigInteger, SmallInteger, String, Boolean, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from backend.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger)
    gender: Mapped[str | None] = mapped_column(String(16))
    game_primary: Mapped[str] = mapped_column(String(32), nullable=False)
    playstyle_tags: Mapped[list | dict] = mapped_column(JSONB, server_default='[]')
    behavior_tags: Mapped[list | dict] = mapped_column(JSONB, server_default='[]')
    bio_text: Mapped[str | None] = mapped_column(Text)
    photo_file_id: Mapped[str | None] = mapped_column(String(256))
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
