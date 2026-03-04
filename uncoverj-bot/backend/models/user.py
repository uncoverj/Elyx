from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, server_default="FALSE")
    premium_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trust_score: Mapped[float] = mapped_column(Float, default=100.0, server_default="100.0")
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="FALSE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now())

    # Связи (будут добавлены по мере создания других моделей)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    accounts: Mapped[List["AccountLink"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    stats: Mapped[List["StatsSnapshot"]] = relationship(back_populates="user", cascade="all, delete-orphan")
