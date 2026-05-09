from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    middlename = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    goal = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    gender = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    is_online = Column(Boolean, nullable=False, default=False)


class Friendship(Base):
    """Directed friendship row.

    - requester_id: who sent the request
    - addressee_id: who received it
    - status: 'pending' | 'accepted'

    A pair (requester, addressee) is unique.  Order matters at request time
    but acceptance is symmetric (both users are friends once accepted).
    """

    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    addressee_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])

    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
        CheckConstraint("requester_id != addressee_id", name="ck_friendship_no_self"),
    )


class Challenge(Base):
    """A head-to-head challenge between two friends.

    Lifecycle:  pending -> accepted -> completed  (or declined / expired)
    Results are hidden until both participants submit or the deadline passes.
    """

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    opponent_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    challenge_type = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    muscle_group = Column(String, nullable=True)
    endurance_mode = Column(String, nullable=True)
    endurance_speed = Column(Float, nullable=True)
    endurance_gradient = Column(Float, nullable=True)
    target_weight_kg = Column(Float, nullable=True)

    status = Column(String, nullable=False, default="pending")

    challenger_result = Column(Text, nullable=True)
    opponent_result = Column(Text, nullable=True)
    challenger_submitted_at = Column(DateTime(timezone=True), nullable=True)
    opponent_submitted_at = Column(DateTime(timezone=True), nullable=True)

    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    deadline_notified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    challenger = relationship("User", foreign_keys=[challenger_id])
    opponent = relationship("User", foreign_keys=[opponent_id])
    winner = relationship("User", foreign_keys=[winner_id])

    __table_args__ = (CheckConstraint("challenger_id != opponent_id", name="ck_challenge_no_self"),)
