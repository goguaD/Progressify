from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models import Meal, MealRating, MealView


class MealRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, meal_id: int) -> Meal | None:
        return self.db.query(Meal).filter(Meal.id == meal_id).first()

    def list_meals(
        self,
        *,
        goal: str | None = None,
        sort: str = "newest",
        limit: int = 50,
        offset: int = 0,
    ) -> list[Meal]:
        q = self.db.query(Meal)
        if goal:
            q = q.filter(Meal.goal == goal)

        if sort == "oldest":
            q = q.order_by(asc(Meal.created_at))
        elif sort == "rating":
            q = q.order_by(desc(Meal.rating_count), desc(Meal.rating_sum))
        elif sort == "views":
            q = q.order_by(desc(Meal.views))
        else:
            q = q.order_by(desc(Meal.created_at))

        return q.offset(offset).limit(limit).all()

    def get_user_rating(self, meal_id: int, user_id: int) -> MealRating | None:
        return (
            self.db.query(MealRating)
            .filter(MealRating.meal_id == meal_id, MealRating.user_id == user_id)
            .first()
        )

    def has_user_viewed(self, meal_id: int, user_id: int) -> bool:
        return (
            self.db.query(MealView)
            .filter(MealView.meal_id == meal_id, MealView.user_id == user_id)
            .first()
            is not None
        )

    def record_view(self, meal_id: int, user_id: int) -> bool:
        """Record a view. Returns True if this was a new view, False if already viewed."""
        if self.has_user_viewed(meal_id, user_id):
            return False
        self.db.add(MealView(meal_id=meal_id, user_id=user_id))
        return True

    def create(self, meal: Meal) -> Meal:
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)
        return meal

    def save(self) -> None:
        self.db.commit()

    def refresh(self, meal: Meal) -> None:
        self.db.refresh(meal)

    def add_rating(self, rating: MealRating) -> MealRating:
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating
