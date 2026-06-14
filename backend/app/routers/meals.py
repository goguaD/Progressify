import uuid
from pydantic import BaseModel

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import ALLOWED_AVATAR_TYPES, MAX_AVATAR_BYTES, MEAL_IMG_DIR
from app.database import get_db
from app.deps import get_current_user
from app.models import Meal, MealRating, Report, User
from app.repositories.meal_repo import MealRepository
from app.schemas import MEAL_GOALS, MealOut, MealRateRequest
from app.services.meal_service import meal_out_dict


class ReportRequest(BaseModel):
    reason: str
    notes: str | None = None

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


@router.post("", response_model=MealOut)
async def create_meal(
    name: str = Form(...),
    description: str = Form(...),
    goal: str = Form(...),
    calories: int = Form(...),
    protein: float = Form(...),
    carbs: float = Form(...),
    fat: float = Form(...),
    fiber: float | None = Form(None),
    sugar: float | None = Form(None),
    name_ka: str | None = Form(None),
    description_ka: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    if goal not in MEAL_GOALS:
        valid = ", ".join(sorted(MEAL_GOALS))
        raise HTTPException(status_code=422, detail=f"Goal must be one of: {valid}")

    image_url = None
    if image and image.filename:
        if image.content_type not in ALLOWED_AVATAR_TYPES:
            raise HTTPException(status_code=422, detail="Image must be PNG, JPEG, or WebP.")
        contents = await image.read()
        if len(contents) > MAX_AVATAR_BYTES:
            raise HTTPException(status_code=422, detail="Image must be 5 MB or smaller.")
        ext = ALLOWED_AVATAR_TYPES[image.content_type]
        fname = f"{uuid.uuid4().hex}{ext}"
        MEAL_IMG_DIR.mkdir(parents=True, exist_ok=True)
        with open(MEAL_IMG_DIR / fname, "wb") as f:
            f.write(contents)
        image_url = f"/static/meals/{fname}"

    meal = Meal(
        name=name,
        name_ka=name_ka or None,
        description=description,
        description_ka=description_ka or None,
        image_url=image_url,
        goal=goal,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fiber=fiber,
        sugar=sugar,
        added_by=current.id,
        is_default=False,
    )
    repo = MealRepository(db)
    repo.create(meal)
    return meal_out_dict(meal, None)


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


@router.delete("/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = MealRepository(db)
    meal = repo.get_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    if current.role != "admin" and meal.added_by != current.id:
        raise HTTPException(status_code=403, detail="You can only delete your own meals")
    db.delete(meal)
    db.commit()
    return {"ok": True}


@router.post("/{meal_id}/report")
def report_meal(
    meal_id: int,
    body: ReportRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = MealRepository(db)
    meal = repo.get_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    report = Report(
        reporter_id=current.id,
        target_type="meal",
        target_id=meal_id,
        target_name=meal.name,
        reason=body.reason,
        notes=body.notes,
    )
    db.add(report)
    db.commit()
    return {"ok": True}


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
