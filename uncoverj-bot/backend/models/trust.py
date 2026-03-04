from datetime import datetime
from sqlalchemy import BigInteger, SmallInteger, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class TrustVote(Base):
    __tablename__ = "trust_votes"
    __table_args__ = (
        UniqueConstraint("voter_id", "target_id", name="uq_trust_votes_voter_target"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    voter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vote: Mapped[int] = mapped_column(SmallInteger)  # +1 или -1
    weight: Mapped[float] = mapped_column(Float, default=1.0, server_default="1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
