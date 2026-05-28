from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, selectinload

from app.models import (
    UserActiveWorkoutPlan,
    UserOneRepMax,
    WorkoutPlan,
    WorkoutPlanRating,
    WorkoutPlanView,
)


class WorkoutRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, plan_id: int) -> WorkoutPlan | None:
        return (
            self.db.query(WorkoutPlan)
            .options(selectinload(WorkoutPlan.days))
            .filter(WorkoutPlan.id == plan_id)
            .first()
        )

    def list_plans(
        self,
        *,
        days_per_week: int | None = None,
        level: str | None = None,
        sort: str = "newest",
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkoutPlan]:
        q = self.db.query(WorkoutPlan)
        if days_per_week is not None:
            q = q.filter(WorkoutPlan.days_per_week == days_per_week)
        if level:
            q = q.filter(WorkoutPlan.level == level)

        if sort == "views":
            q = q.order_by(desc(WorkoutPlan.views))
        elif sort == "oldest":
            q = q.order_by(asc(WorkoutPlan.created_at))
        else:
            q = q.order_by(desc(WorkoutPlan.created_at))

        return q.offset(offset).limit(limit).all()

    # ── Views (unique per user) ──────────────────────────────────────────

    def has_user_viewed(self, plan_id: int, user_id: int) -> bool:
        return (
            self.db.query(WorkoutPlanView)
            .filter(
                WorkoutPlanView.plan_id == plan_id,
                WorkoutPlanView.user_id == user_id,
            )
            .first()
            is not None
        )

    def record_view(self, plan_id: int, user_id: int) -> bool:
        """Record a view. Returns True if new, False if already viewed."""
        if self.has_user_viewed(plan_id, user_id):
            return False
        self.db.add(WorkoutPlanView(plan_id=plan_id, user_id=user_id))
        return True

    # ── Ratings ──────────────────────────────────────────────────────────

    def get_user_rating(
        self, plan_id: int, user_id: int,
    ) -> WorkoutPlanRating | None:
        return (
            self.db.query(WorkoutPlanRating)
            .filter(
                WorkoutPlanRating.plan_id == plan_id,
                WorkoutPlanRating.user_id == user_id,
            )
            .first()
        )

    def add_rating(self, rating: WorkoutPlanRating) -> WorkoutPlanRating:
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    # ── Helpers ──────────────────────────────────────────────────────────

    def create(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def save(self) -> None:
        self.db.commit()

    def refresh(self, plan: WorkoutPlan) -> None:
        self.db.refresh(plan)

    # ── Active plan per user ────────────────────────────────────────────

    def get_active_plan(self, user_id: int) -> UserActiveWorkoutPlan | None:
        return (
            self.db.query(UserActiveWorkoutPlan)
            .filter(UserActiveWorkoutPlan.user_id == user_id)
            .first()
        )

    def set_active_plan(self, user_id: int, plan_id: int) -> UserActiveWorkoutPlan:
        existing = self.get_active_plan(user_id)
        if existing:
            existing.plan_id = plan_id
            self.db.commit()
            self.db.refresh(existing)
            return existing
        row = UserActiveWorkoutPlan(user_id=user_id, plan_id=plan_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_active_plan(self, user_id: int) -> None:
        self.db.query(UserActiveWorkoutPlan).filter(
            UserActiveWorkoutPlan.user_id == user_id,
        ).delete()
        self.db.commit()

    # ── 1RM lifts per user ──────────────────────────────────────────────

    def list_one_rep_maxes(self, user_id: int) -> list[UserOneRepMax]:
        return (
            self.db.query(UserOneRepMax)
            .filter(UserOneRepMax.user_id == user_id)
            .all()
        )

    def upsert_one_rep_max(
        self, user_id: int, exercise_name: str, weight_kg: float,
    ) -> UserOneRepMax:
        row = (
            self.db.query(UserOneRepMax)
            .filter(
                UserOneRepMax.user_id == user_id,
                UserOneRepMax.exercise_name == exercise_name,
            )
            .first()
        )
        if row:
            row.weight_kg = weight_kg
        else:
            row = UserOneRepMax(
                user_id=user_id,
                exercise_name=exercise_name,
                weight_kg=weight_kg,
            )
            self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def bulk_upsert_one_rep_max(
        self, user_id: int, lifts: list[tuple[str, float]],
    ) -> list[UserOneRepMax]:
        existing: dict[str, UserOneRepMax] = {
            str(r.exercise_name): r for r in self.list_one_rep_maxes(user_id)
        }
        result: list[UserOneRepMax] = []
        for name, weight in lifts:
            row = existing.get(name)
            if row:
                row.weight_kg = weight
            else:
                row = UserOneRepMax(
                    user_id=user_id,
                    exercise_name=name,
                    weight_kg=weight,
                )
                self.db.add(row)
            result.append(row)
        self.db.commit()
        for r in result:
            self.db.refresh(r)
        return result
