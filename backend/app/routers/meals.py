from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Meal, MealRating, User
from app.repositories.meal_repo import MealRepository
from app.schemas import MealOut, MealRateRequest
from app.services.meal_service import meal_out_dict

router = APIRouter(prefix="/meals", tags=["meals"])


@router.get("", response_model=list[MealOut])
def list_meals(
    goal: str | None = Query(None),
    sort: str = Query("newest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    repo = MealRepository(db)
    meals = repo.list_meals(goal=goal, sort=sort, limit=limit, offset=offset)
    result = []
    for m in meals:
        my = repo.get_user_rating(m.id, current.id)
        result.append(meal_out_dict(m, my.score if my else None))
    return result


@router.get("/{meal_id}", response_model=MealOut)
def get_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = MealRepository(db)
    meal = repo.get_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    my = repo.get_user_rating(meal.id, current.id)
    return meal_out_dict(meal, my.score if my else None)


@router.post("/{meal_id}/view", response_model=MealOut)
def record_view(
    meal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = MealRepository(db)
    meal = repo.get_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    is_new = repo.record_view(meal_id, current.id)
    if is_new:
        meal.views = (meal.views or 0) + 1
    repo.save()
    repo.refresh(meal)

    my = repo.get_user_rating(meal.id, current.id)
    return meal_out_dict(meal, my.score if my else None)


@router.post("/{meal_id}/rate", response_model=MealOut)
def rate_meal(
    meal_id: int,
    body: MealRateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = MealRepository(db)
    meal = repo.get_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    existing = repo.get_user_rating(meal_id, current.id)
    if existing:
        old_score = existing.score
        existing.score = body.score
        meal.rating_sum = (meal.rating_sum or 0) - old_score + body.score
    else:
        rating = MealRating(meal_id=meal_id, user_id=current.id, score=body.score)
        repo.add_rating(rating)
        meal.rating_sum = (meal.rating_sum or 0) + body.score
        meal.rating_count = (meal.rating_count or 0) + 1

    repo.save()
    repo.refresh(meal)
    return meal_out_dict(meal, body.score)
