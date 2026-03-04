from sqlalchemy import BigInteger, SmallInteger, Float, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from backend.database import Base

class TrustVote(Base):
    __tablename__ = "trust_votes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    voter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    vote: Mapped[int | None] = mapped_column(SmallInteger)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('voter_id', 'target_id', name='_trust_vote_uc'),
    )
