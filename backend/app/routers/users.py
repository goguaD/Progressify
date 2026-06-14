import contextlib
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import ALLOWED_AVATAR_TYPES, AVATAR_DIR, MAX_AVATAR_BYTES
from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import User
from app.repositories.friend_repo import FriendRepository
from app.repositories.user_repo import UserRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas import AdminUserOut, ProfileView, PublicUser, UserOut
from app.services.friend_service import friendship_state
from app.services.strength_standards import (
    STRENGTH_STANDARDS,
    classify_lift,
    compute_muscle_levels,
    unit_hint,
)
from app.services.user_service import (
    placeholder_activity,
    public_user_dict,
)
from app.services.workout_service import plan_summary_dict

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> User:
    """Return current user.  Used as a heartbeat -- get_current_user
    automatically bumps last_seen."""
    return current


@router.get("/users/search", response_model=list[PublicUser])
def search_users(
    q: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    needle = q.strip().lower()
    if not needle:
        return []
    repo = UserRepository(db)
    rows = repo.search_by_username(needle, current.id, hide_admins=(current.role != "admin"))
    return [public_user_dict(u) for u in rows]


@router.get("/users/by-username/{username}", response_model=ProfileView)
def get_profile(
    username: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)

    user = user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and current.role != "admin" and user.id != current.id:
        raise HTTPException(status_code=404, detail="User not found")

    state, req_id = friendship_state(friend_repo, current.id, user.id)
    activity = placeholder_activity(user)

    workout_repo = WorkoutRepository(db)
    active = workout_repo.get_active_plan(user.id)
    lifts_rows = workout_repo.list_one_rep_maxes(user.id) if active else []

    base = public_user_dict(user)
    base["relationship"] = state
    base["pending_request_id"] = req_id
    base["friend_count"] = len(friend_repo.accepted_friend_ids(user.id))
    base["current_workout"] = activity["current_workout"]
    base["current_meal_plan"] = activity["current_meal_plan"]
    base["last_workout_text"] = activity["last_activity"]

    muscle_levels: dict[str, str] = {}
    active_workout: dict | None = None
    if active:
        plan = workout_repo.get_by_id(active.plan_id)
        if plan:
            raw_lifts = [
                {"exercise_name": r.exercise_name, "weight_kg": r.weight_kg}
                for r in lifts_rows
            ]
            muscle_levels = compute_muscle_levels(
                raw_lifts, user.weight, user.gender or "male",
            )
            by_name = {r.exercise_name: r for r in lifts_rows}
            seen: set[str] = set()
            lifts_summary: list[dict] = []
            for day in plan.days:
                for ex in day.exercises:
                    if ex.name in seen:
                        continue
                    seen.add(ex.name)
                    row = by_name.get(ex.name)
                    level = None
                    if row and user.weight and user.gender:
                        level = classify_lift(
                            ex.name, row.weight_kg, user.weight, user.gender,
                        )
                    lifts_summary.append({
                        "exercise_name": ex.name,
                        "weight_kg": row.weight_kg if row else 0.0,
                        "muscle_group": ex.muscle_group,
                        "level": level,
                        "has_standard": ex.name in STRENGTH_STANDARDS,
                        "unit_hint": unit_hint(ex.name, "en"),
                        "unit_hint_ka": unit_hint(ex.name, "ka"),
                    })
            active_workout = {
                "plan": plan_summary_dict(plan, None),
                "lifts": lifts_summary,
            }

    base["muscle_levels"] = muscle_levels
    base["active_workout"] = active_workout
    return base


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> User:
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Avatar must be a PNG, JPEG, or WebP image.",
        )

    contents = await file.read()
    if len(contents) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="Avatar must be 5 MB or smaller.")
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")

    for old in AVATAR_DIR.glob(f"{current.id}.*"):
        with contextlib.suppress(OSError):
            old.unlink()

    ext = ALLOWED_AVATAR_TYPES[file.content_type]
    cache_bust = uuid.uuid4().hex[:8]
    fname = f"{current.id}{ext}"
    out_path = AVATAR_DIR / fname
    with open(out_path, "wb") as f:
        f.write(contents)

    current.avatar_url = f"/static/avatars/{fname}?v={cache_bust}"
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me/avatar", response_model=UserOut)
def delete_avatar(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> User:
    for old in AVATAR_DIR.glob(f"{current.id}.*"):
        with contextlib.suppress(OSError):
            old.unlink()
    current.avatar_url = None
    db.commit()
    db.refresh(current)
    return current


@router.get("/admin/users", response_model=list[AdminUserOut])
def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    return UserRepository(db).list_all()


@router.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
) -> dict:
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    repo = UserRepository(db)
    target = repo.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(target)
    db.commit()
    return {"ok": True}


@router.delete("/admin/meals/{meal_id}")
def admin_delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    from app.models import Meal
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(meal)
    db.commit()
    return {"ok": True}


@router.delete("/admin/workouts/{plan_id}")
def admin_delete_workout(
    plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    from app.models import WorkoutPlan
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    db.delete(plan)
    db.commit()
    return {"ok": True}


@router.get("/admin/reports")
def admin_get_reports(
    reviewed: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    from app.models import Report
    rows = (
        db.query(Report)
        .filter(Report.reviewed == reviewed)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "reporter_username": r.reporter.username if r.reporter else None,
            "target_type": r.target_type,
            "target_id": r.target_id,
            "target_name": r.target_name,
            "reason": r.reason,
            "notes": r.notes,
            "reviewed": r.reviewed,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.patch("/admin/reports/{report_id}/reviewed")
def admin_mark_report_reviewed(
    report_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    from app.models import Report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.reviewed = True
    db.commit()
    return {"ok": True}
