from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base

class Swipe(Base):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    game: Mapped[str | None] = mapped_column(String(32))
    action: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_swipes_from', 'from_user_id', 'game'),
    )
