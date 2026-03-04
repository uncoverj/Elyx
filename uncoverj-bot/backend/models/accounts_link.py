from sqlalchemy import BigInteger, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class AccountLink(Base):
    __tablename__ = "accounts_link"
    __table_args__ = (
        UniqueConstraint("user_id", "game", name="uq_accounts_link_user_game"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    game: Mapped[str] = mapped_column(String(32), nullable=False)
    game_id: Mapped[str] = mapped_column(String(128), nullable=False)  # 'nickname#tag' or steam64
    verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="FALSE")

    user: Mapped["User"] = relationship(back_populates="accounts")
