from sqlalchemy import BigInteger, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base

class AccountsLink(Base):
    __tablename__ = "accounts_link"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    game: Mapped[str] = mapped_column(String(32), nullable=False)
    game_id: Mapped[str] = mapped_column(String(128), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (UniqueConstraint('user_id', 'game', name='_user_game_uc'),)
