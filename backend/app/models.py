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


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_ka = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    description_ka = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    goal = Column(String, nullable=False, index=True)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    views = Column(Integer, nullable=False, default=0)
    rating_sum = Column(Float, nullable=False, default=0.0)
    rating_count = Column(Integer, nullable=False, default=0)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", foreign_keys=[added_by])
    ratings = relationship("MealRating", back_populates="meal", cascade="all, delete-orphan")
    user_views = relationship("MealView", back_populates="meal", cascade="all, delete-orphan")


class MealRating(Base):
    __tablename__ = "meal_ratings"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(
        Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meal = relationship("Meal", back_populates="ratings")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("meal_id", "user_id", name="uq_meal_rating_user"),
        CheckConstraint("score >= 0 AND score <= 5", name="ck_rating_range"),
    )


class MealView(Base):
    __tablename__ = "meal_views"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(
        Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meal = relationship("Meal", back_populates="user_views")

    __table_args__ = (
        UniqueConstraint("meal_id", "user_id", name="uq_meal_view_user"),
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_ka = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    description_ka = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    days_per_week = Column(Integer, nullable=False, index=True)
    split_type = Column(String, nullable=False)
    level = Column(String, nullable=False, default="intermediate")
    views = Column(Integer, nullable=False, default=0)
    rating_sum = Column(Float, nullable=False, default=0.0)
    rating_count = Column(Integer, nullable=False, default=0)
    is_default = Column(Boolean, nullable=False, default=False)
    added_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    days = relationship(
        "WorkoutDay",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="WorkoutDay.day_number",
    )
    author = relationship("User", foreign_keys=[added_by])
    ratings = relationship(
        "WorkoutPlanRating",
        back_populates="plan",
        cascade="all, delete-orphan",
    )
    user_views = relationship(
        "WorkoutPlanView",
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(
        Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    day_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    name_ka = Column(String, nullable=True)
    focus = Column(String, nullable=True)

    plan = relationship("WorkoutPlan", back_populates="days")
    exercises = relationship(
        "Exercise",
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="Exercise.order_index",
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(
        Integer, ForeignKey("workout_days.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    order_index = Column(Integer, nullable=False, default=0)
    name = Column(String, nullable=False)
    name_ka = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    description_ka = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    sets = Column(Integer, nullable=False, default=3)
    rep_low = Column(Integer, nullable=False, default=8)
    rep_high = Column(Integer, nullable=False, default=12)
    rest_seconds = Column(Integer, nullable=False, default=90)
    primary_purpose = Column(String, nullable=False, default="hypertrophy")
    muscle_group = Column(String, nullable=False, default="general")
    # JSON-encoded list of {"slug": str, "intensity": "low"|"medium"|"high"}.
    # When present, it overrides the default EXERCISE_MUSCLES lookup so user-
    # submitted exercises can specify exactly which muscles they target and at
    # what intensity (drives the muscle-map shading on the frontend).
    muscle_targets = Column(Text, nullable=True)

    day = relationship("WorkoutDay", back_populates="exercises")


class WorkoutPlanRating(Base):
    __tablename__ = "workout_plan_ratings"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(
        Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("WorkoutPlan", back_populates="ratings")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("plan_id", "user_id", name="uq_wplan_rating_user"),
        CheckConstraint(
            "score >= 0 AND score <= 5", name="ck_wplan_rating_range",
        ),
    )


class WorkoutPlanView(Base):
    __tablename__ = "workout_plan_views"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(
        Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("WorkoutPlan", back_populates="user_views")

    __table_args__ = (
        UniqueConstraint("plan_id", "user_id", name="uq_wplan_view_user"),
    )


class UserActiveWorkoutPlan(Base):
    """The single workout plan a user has adopted as their training programme."""

    __tablename__ = "user_active_workout_plans"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    plan_id = Column(
        Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now(),
    )

    user = relationship("User")
    plan = relationship("WorkoutPlan")


class UserOneRepMax(Base):
    """A user-reported one-rep-max (1RM) for an exercise, in kilograms.

    Keyed by ``exercise_name`` rather than ``exercise_id`` because the same
    movement (e.g. Barbell Bench Press) may appear in multiple days of the
    plan as separate rows but represents a single lift for the lifter.
    """

    __tablename__ = "user_one_rep_max"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    exercise_name = Column(String, nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "exercise_name", name="uq_user_exercise_1rm",
        ),
    )


class MuscleAchievement(Base):
    """Recorded when a user's strength level for a muscle group increases."""

    __tablename__ = "muscle_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    muscle_slug = Column(String, nullable=False)
    old_level = Column(String, nullable=True)
    new_level = Column(String, nullable=False)
    achieved_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
