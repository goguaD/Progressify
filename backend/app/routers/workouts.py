import json
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import ALLOWED_AVATAR_TYPES, MAX_AVATAR_BYTES, WORKOUT_IMG_DIR
from app.database import get_db
from app.deps import get_current_user
from app.models import Exercise, MuscleAchievement, User, WorkoutDay, WorkoutPlan, WorkoutPlanRating
from app.repositories.workout_repo import WorkoutRepository
from app.schemas import (
    ActivePlanOut,
    SetActivePlanRequest,
    UpdateLiftsRequest,
    WorkoutPlanCreate,
    WorkoutPlanDetail,
    WorkoutPlanOut,
    WorkoutRateRequest,
)
from app.services.strength_standards import (
    EXERCISE_MUSCLES,
    STRENGTH_STANDARDS,
    classify_lift,
    compute_muscle_levels,
    unit_hint,
)
from app.services.workout_service import plan_detail_dict, plan_summary_dict

router = APIRouter(prefix="/workouts", tags=["workouts"])
me_router = APIRouter(prefix="/me/workout-plan", tags=["my-workout-plan"])

_LEVEL_RANK: dict[str, int] = {"beginner": 0, "intermediate": 1, "advanced": 2, "elite": 3}


def _emit_muscle_achievements(
    db: Session,
    user: User,
    old_levels: dict[str, str],
    new_levels: dict[str, str],
) -> None:
    """Insert MuscleAchievement rows for any muscle that levelled up."""
    for slug, new_lvl in new_levels.items():
        old_lvl = old_levels.get(slug)
        old_rank = _LEVEL_RANK.get(old_lvl, -1) if old_lvl else -1
        new_rank = _LEVEL_RANK.get(new_lvl, -1)
        if new_rank > old_rank:
            db.add(MuscleAchievement(
                user_id=user.id,
                muscle_slug=slug,
                old_level=old_lvl,
                new_level=new_lvl,
            ))
    db.commit()


def _build_active_plan_response(
    db: Session, user: User,
) -> dict | None:
    """Assemble an ActivePlanOut payload for the given user, or None."""
    repo = WorkoutRepository(db)
    active = repo.get_active_plan(user.id)
    if not active:
        return None
    plan = repo.get_by_id(active.plan_id)
    if not plan:
        return None

    lifts_rows = repo.list_one_rep_maxes(user.id)
    by_name = {r.exercise_name: r for r in lifts_rows}

    # Build the lifts list in the order the plan exposes them, deduped.
    seen: set[str] = set()
    lifts: list[dict] = []
    for day in plan.days:
        for ex in day.exercises:
            if ex.name in seen:
                continue
            seen.add(ex.name)
            row = by_name.get(ex.name)
            weight = row.weight_kg if row else 0.0
            level = None
            if row and user.weight and user.gender:
                level = classify_lift(
                    ex.name, row.weight_kg, user.weight, user.gender,
                )
            lifts.append({
                "exercise_name": ex.name,
                "weight_kg": weight,
                "muscle_group": ex.muscle_group,
                "level": level,
                "has_standard": ex.name in STRENGTH_STANDARDS,
                "unit_hint": unit_hint(ex.name, "en"),
                "unit_hint_ka": unit_hint(ex.name, "ka"),
            })

    raw_lifts = [
        {"exercise_name": r.exercise_name, "weight_kg": r.weight_kg}
        for r in lifts_rows
    ]
    muscle_levels = compute_muscle_levels(
        raw_lifts, user.weight, user.gender or "male",
    )

    return {
        "plan": plan_detail_dict(plan, None),
        "lifts": lifts,
        "muscle_levels": muscle_levels,
        "bodyweight_kg": user.weight,
    }


@router.get("", response_model=list[WorkoutPlanOut])
def list_plans(
    days_per_week: int | None = Query(None, ge=1, le=7),
    level: str | None = Query(None),
    sort: str = Query("newest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    repo = WorkoutRepository(db)
    plans = repo.list_plans(
        days_per_week=days_per_week,
        level=level,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    result = []
    for p in plans:
        my = repo.get_user_rating(p.id, current.id)
        result.append(plan_summary_dict(p, my.score if my else None))
    return result


@router.post("", response_model=WorkoutPlanDetail)
async def create_plan(
    payload: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    """Create a user-submitted workout plan.

    ``payload`` is a JSON string conforming to :class:`WorkoutPlanCreate`. The
    image is optional and stored under ``/static/workouts``.
    """
    try:
        data = json.loads(payload)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="payload must be valid JSON") from None
    try:
        spec = WorkoutPlanCreate.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    if len(spec.days) != spec.days_per_week:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Provided {len(spec.days)} day(s) but days_per_week is "
                f"{spec.days_per_week}."
            ),
        )
    for day in spec.days:
        if not day.exercises:
            raise HTTPException(
                status_code=422,
                detail=f"Day {day.day_number} must include at least one exercise.",
            )
        for ex in day.exercises:
            if ex.rep_low > ex.rep_high:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Exercise '{ex.name}': rep_low cannot exceed rep_high."
                    ),
                )

    image_url: str | None = None
    if image and image.filename:
        if image.content_type not in ALLOWED_AVATAR_TYPES:
            raise HTTPException(
                status_code=422,
                detail="Image must be PNG, JPEG, or WebP.",
            )
        contents = await image.read()
        if len(contents) > MAX_AVATAR_BYTES:
            raise HTTPException(
                status_code=422, detail="Image must be 5 MB or smaller.",
            )
        ext = ALLOWED_AVATAR_TYPES[image.content_type]
        fname = f"{uuid.uuid4().hex}{ext}"
        WORKOUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
        with open(WORKOUT_IMG_DIR / fname, "wb") as f:
            f.write(contents)
        image_url = f"/static/workouts/{fname}"

    plan = WorkoutPlan(
        name=spec.name.strip() or (spec.name_ka or "").strip(),
        name_ka=spec.name_ka.strip() if spec.name_ka else None,
        description=spec.description or "",
        description_ka=spec.description_ka or None,
        image_url=image_url,
        days_per_week=spec.days_per_week,
        split_type=spec.split_type or "custom",
        level=spec.level,
        is_default=False,
        added_by=current.id,
    )

    for day_spec in spec.days:
        day = WorkoutDay(
            day_number=day_spec.day_number,
            name=day_spec.name,
            name_ka=day_spec.name_ka,
            focus=day_spec.focus,
        )
        for idx, ex_spec in enumerate(day_spec.exercises):
            day.exercises.append(
                Exercise(
                    order_index=idx,
                    name=ex_spec.name,
                    name_ka=ex_spec.name_ka,
                    description=ex_spec.description or "",
                    description_ka=ex_spec.description_ka,
                    sets=ex_spec.sets,
                    rep_low=ex_spec.rep_low,
                    rep_high=ex_spec.rep_high,
                    rest_seconds=ex_spec.rest_seconds,
                    primary_purpose=ex_spec.primary_purpose,
                    muscle_group=ex_spec.muscle_group,
                    muscle_targets=(
                        json.dumps([t.model_dump() for t in ex_spec.muscle_targets])
                        if ex_spec.muscle_targets else None
                    ),
                ),
            )
        plan.days.append(day)

    repo = WorkoutRepository(db)
    repo.create(plan)
    loaded = repo.get_by_id(plan.id)
    if not loaded:
        raise HTTPException(status_code=500, detail="Failed to load created plan")
    return plan_detail_dict(loaded, None)


@router.get("/{plan_id}", response_model=WorkoutPlanDetail)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = WorkoutRepository(db)
    plan = repo.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    my = repo.get_user_rating(plan.id, current.id)
    return plan_detail_dict(plan, my.score if my else None)


@router.post("/{plan_id}/view", response_model=WorkoutPlanDetail)
def record_view(
    plan_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = WorkoutRepository(db)
    plan = repo.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    is_new = repo.record_view(plan_id, current.id)
    if is_new:
        plan.views = (plan.views or 0) + 1
    repo.save()
    repo.refresh(plan)

    my = repo.get_user_rating(plan.id, current.id)
    return plan_detail_dict(plan, my.score if my else None)


@router.post("/{plan_id}/rate", response_model=WorkoutPlanDetail)
def rate_plan(
    plan_id: int,
    body: WorkoutRateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = WorkoutRepository(db)
    plan = repo.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    existing = repo.get_user_rating(plan_id, current.id)
    if existing:
        old_score = existing.score
        existing.score = body.score
        plan.rating_sum = (plan.rating_sum or 0) - old_score + body.score
    else:
        rating = WorkoutPlanRating(
            plan_id=plan_id, user_id=current.id, score=body.score,
        )
        repo.add_rating(rating)
        plan.rating_sum = (plan.rating_sum or 0) + body.score
        plan.rating_count = (plan.rating_count or 0) + 1

    repo.save()
    repo.refresh(plan)
    return plan_detail_dict(plan, body.score)


# ── /me/workout-plan endpoints ───────────────────────────────────────────────

@me_router.get("", response_model=ActivePlanOut | None)
def my_active_plan(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict | None:
    return _build_active_plan_response(db, current)


@me_router.post("", response_model=ActivePlanOut)
def set_my_active_plan(
    body: SetActivePlanRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = WorkoutRepository(db)
    plan = repo.get_by_id(body.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    # Snapshot old muscle levels before any changes
    old_lifts_rows = repo.list_one_rep_maxes(current.id)
    old_raw = [{"exercise_name": r.exercise_name, "weight_kg": r.weight_kg} for r in old_lifts_rows]
    old_levels = compute_muscle_levels(old_raw, current.weight, current.gender or "male")

    repo.set_active_plan(current.id, body.plan_id)
    if body.lifts:
        repo.bulk_upsert_one_rep_max(
            current.id,
            [(lift.exercise_name, lift.weight_kg) for lift in body.lifts],
        )

    # Compute new levels and emit achievements for any level-ups
    new_lifts_rows = repo.list_one_rep_maxes(current.id)
    new_raw = [{"exercise_name": r.exercise_name, "weight_kg": r.weight_kg} for r in new_lifts_rows]
    new_levels = compute_muscle_levels(new_raw, current.weight, current.gender or "male")
    _emit_muscle_achievements(db, current, old_levels, new_levels)

    response = _build_active_plan_response(db, current)
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to load active plan")
    return response


@me_router.patch("/lifts", response_model=ActivePlanOut)
def update_my_lifts(
    body: UpdateLiftsRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = WorkoutRepository(db)
    if not repo.get_active_plan(current.id):
        raise HTTPException(
            status_code=400,
            detail="No active workout plan. Choose a plan before setting lifts.",
        )

    # Snapshot old muscle levels before changes
    old_lifts_rows = repo.list_one_rep_maxes(current.id)
    old_raw = [{"exercise_name": r.exercise_name, "weight_kg": r.weight_kg} for r in old_lifts_rows]
    old_levels = compute_muscle_levels(old_raw, current.weight, current.gender or "male")

    repo.bulk_upsert_one_rep_max(
        current.id,
        [(lift.exercise_name, lift.weight_kg) for lift in body.lifts],
    )

    # Emit achievements for any level-ups
    new_lifts_rows = repo.list_one_rep_maxes(current.id)
    new_raw = [{"exercise_name": r.exercise_name, "weight_kg": r.weight_kg} for r in new_lifts_rows]
    new_levels = compute_muscle_levels(new_raw, current.weight, current.gender or "male")
    _emit_muscle_achievements(db, current, old_levels, new_levels)

    response = _build_active_plan_response(db, current)
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to load active plan")
    return response


@me_router.delete("", status_code=204)
def remove_my_active_plan(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    repo = WorkoutRepository(db)
    repo.delete_active_plan(current.id)


_ = EXERCISE_MUSCLES  # re-exported for convenience; silences unused import lint
