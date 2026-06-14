from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Challenge,
    Meal,
    MealView,
    MuscleAchievement,
    Report,
    User,
    UserOneRepMax,
    WorkoutPlan,
    WorkoutPlanView,
)
from app.repositories.friend_repo import FriendRepository
from app.services.challenge_service import challenge_user_brief, parse_result, safe_deadline
from app.services.meal_service import meal_out_dict
from app.services.strength_standards import EXERCISE_MUSCLES, classify_lift
from app.services.user_service import is_online, public_user_dict
from app.services.workout_service import plan_summary_dict

router = APIRouter(prefix="/feed", tags=["feed"])
notif_router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def get_feed(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    friend_repo = FriendRepository(db)
    friend_ids = friend_repo.accepted_friend_ids(current.id)

    # Use naive UTC datetimes for SQLite compatibility
    now_naive = datetime.utcnow()
    since_24h = now_naive - timedelta(hours=24)
    since_7d = now_naive - timedelta(days=7)
    since_14d = now_naive - timedelta(days=14)

    # ── Trending meals (unique views in last 24 hours) ─────────────────────
    meal_trend_rows = (
        db.query(MealView.meal_id, func.count(MealView.id).label("cnt"))
        .filter(MealView.created_at >= since_24h)
        .group_by(MealView.meal_id)
        .order_by(func.count(MealView.id).desc())
        .limit(6)
        .all()
    )
    trending_meals: list[dict] = []
    for row in meal_trend_rows:
        meal = db.query(Meal).filter(Meal.id == row.meal_id).first()
        if meal:
            trending_meals.append({"meal": meal_out_dict(meal), "trend_views": row.cnt})

    # ── Trending workouts (unique views in last 24 hours) ──────────────────
    workout_trend_rows = (
        db.query(WorkoutPlanView.plan_id, func.count(WorkoutPlanView.id).label("cnt"))
        .filter(WorkoutPlanView.created_at >= since_24h)
        .group_by(WorkoutPlanView.plan_id)
        .order_by(func.count(WorkoutPlanView.id).desc())
        .limit(6)
        .all()
    )
    trending_workouts: list[dict] = []
    for row in workout_trend_rows:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == row.plan_id).first()
        if plan:
            trending_workouts.append({"workout": plan_summary_dict(plan), "trend_views": row.cnt})

    # ── Timeline items ─────────────────────────────────────────────────────
    items: list[dict] = []

    # New meals added in the last 7 days
    new_meals = (
        db.query(Meal)
        .filter(Meal.created_at >= since_7d)
        .order_by(Meal.created_at.desc())
        .limit(8)
        .all()
    )
    for meal in new_meals:
        ts = meal.created_at
        items.append({
            "type": "new_meal",
            "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
            "meal": meal_out_dict(meal),
        })

    # New workout plans added in the last 7 days
    new_workouts = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.created_at >= since_7d)
        .order_by(WorkoutPlan.created_at.desc())
        .limit(8)
        .all()
    )
    for plan in new_workouts:
        ts = plan.created_at
        items.append({
            "type": "new_workout",
            "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
            "workout": plan_summary_dict(plan),
        })

    if friend_ids:
        friend_id_list = list(friend_ids)

        # Friend 1RM PR updates in the last 7 days
        friend_prs = (
            db.query(UserOneRepMax)
            .filter(
                UserOneRepMax.user_id.in_(friend_id_list),
                UserOneRepMax.updated_at >= since_7d,
                UserOneRepMax.weight_kg > 0,
            )
            .order_by(UserOneRepMax.updated_at.desc())
            .limit(30)
            .all()
        )
        pr_user_cache: dict[int, User] = {}
        pr_public_cache: dict[int, dict] = {}
        for pr in friend_prs:
            if pr.user_id not in pr_user_cache:
                u = db.query(User).filter(User.id == pr.user_id).first()
                if u:
                    pr_user_cache[pr.user_id] = u
                    pr_public_cache[pr.user_id] = public_user_dict(u)
            u_obj = pr_user_cache.get(pr.user_id)
            user_data = pr_public_cache.get(pr.user_id)
            if not user_data or not u_obj:
                continue

            muscle_map = EXERCISE_MUSCLES.get(pr.exercise_name, {})
            primary_muscles = muscle_map.get("primary", [])
            primary_muscle = primary_muscles[0] if primary_muscles else None

            level = None
            if u_obj.weight and u_obj.gender:
                level = classify_lift(
                    pr.exercise_name, pr.weight_kg, u_obj.weight, u_obj.gender,
                )

            ts = pr.updated_at
            items.append({
                "type": "friend_pr",
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "user": user_data,
                "exercise_name": pr.exercise_name,
                "weight_kg": pr.weight_kg,
                "level": level,
                "muscle_group": primary_muscle,
            })

        # Challenges between friends (accepted or completed, last 14 days)
        friend_challenges = (
            db.query(Challenge)
            .filter(
                Challenge.status.in_(["accepted", "completed"]),
                Challenge.updated_at >= since_14d,
                or_(
                    Challenge.challenger_id.in_(friend_id_list),
                    Challenge.opponent_id.in_(friend_id_list),
                ),
            )
            .order_by(Challenge.updated_at.desc())
            .limit(20)
            .all()
        )
        seen_challenge_ids: set[int] = set()
        for ch in friend_challenges:
            if ch.id in seen_challenge_ids:
                continue
            seen_challenge_ids.add(ch.id)

            dl = safe_deadline(ch)
            is_past = dl is not None and datetime.now(UTC) >= dl
            both_submitted = (
                ch.challenger_submitted_at is not None
                and ch.opponent_submitted_at is not None
            )
            reveal = both_submitted or is_past or ch.status == "completed"

            ts = ch.updated_at
            items.append({
                "type": "friend_challenge",
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "challenge_id": ch.id,
                "challenger": challenge_user_brief(ch.challenger),
                "opponent": challenge_user_brief(ch.opponent),
                "challenge_type": ch.challenge_type,
                "message": ch.message,
                "deadline": ch.deadline.isoformat() if ch.deadline else None,
                "status": ch.status,
                "muscle_group": ch.muscle_group,
                "endurance_mode": ch.endurance_mode,
                "endurance_speed": ch.endurance_speed,
                "endurance_gradient": ch.endurance_gradient,
                "target_weight_kg": ch.target_weight_kg,
                "challenger_result": parse_result(ch.challenger_result) if reveal else None,
                "opponent_result": parse_result(ch.opponent_result) if reveal else None,
                "winner": challenge_user_brief(ch.winner) if ch.winner else None,
            })

        # Muscle achievements by friends in the last 7 days
        achievements = (
            db.query(MuscleAchievement)
            .filter(
                MuscleAchievement.user_id.in_(friend_id_list),
                MuscleAchievement.achieved_at >= since_7d,
            )
            .order_by(MuscleAchievement.achieved_at.desc())
            .limit(20)
            .all()
        )
        ach_user_cache: dict[int, dict] = {}
        for ach in achievements:
            if ach.user_id not in ach_user_cache:
                u = db.query(User).filter(User.id == ach.user_id).first()
                if u:
                    ach_user_cache[ach.user_id] = public_user_dict(u)
            user_data = ach_user_cache.get(ach.user_id)
            if not user_data:
                continue
            ts = ach.achieved_at
            items.append({
                "type": "muscle_achievement",
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "user": user_data,
                "muscle_slug": ach.muscle_slug,
                "old_level": ach.old_level,
                "new_level": ach.new_level,
            })

    # Sort all timeline items newest first
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return {
        "trending_meals": trending_meals,
        "trending_workouts": trending_workouts,
        "items": items,
    }


# ── Online friends list ────────────────────────────────────────────────────────

@router.get("/online-friends")
def online_friends(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    """Returns friends list with online status, sorted alphabetically."""
    friend_repo = FriendRepository(db)
    friend_ids = friend_repo.accepted_friend_ids(current.id)
    if not friend_ids:
        return {"online_count": 0, "friends": []}

    friends_data = []
    for fid in friend_ids:
        u = db.query(User).filter(User.id == fid).first()
        if u:
            d = public_user_dict(u)
            friends_data.append(d)

    friends_data.sort(key=lambda f: f["username"].lower())
    online_count = sum(1 for f in friends_data if f["is_online"])

    return {"online_count": online_count, "friends": friends_data}


# ── Notifications ──────────────────────────────────────────────────────────────

@notif_router.get("")
def get_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    """Aggregate notifications for the current user."""
    friend_repo = FriendRepository(db)
    friend_ids = friend_repo.accepted_friend_ids(current.id)
    now_naive = datetime.utcnow()
    since_7d = now_naive - timedelta(days=7)

    notifications: list[dict] = []

    # 1. Pending incoming friend requests (no time limit — always actionable)
    pending_reqs = friend_repo.pending_for_user(current.id)
    for req in pending_reqs:
        ts = req.created_at
        notifications.append({
            "type": "friend_request",
            "id": f"fr_{req.id}",
            "request_id": req.id,
            "from_user": public_user_dict(req.requester),
            "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
            "link": "/friends",
        })

    # 2. Pending challenges where I am the opponent (always actionable)
    pending_challenges = (
        db.query(Challenge)
        .filter(
            Challenge.opponent_id == current.id,
            Challenge.status == "pending",
        )
        .all()
    )
    for ch in pending_challenges:
        ts = ch.created_at
        notifications.append({
            "type": "challenge_received",
            "id": f"ch_recv_{ch.id}",
            "challenge_id": ch.id,
            "from_user": challenge_user_brief(ch.challenger),
            "challenge_type": ch.challenge_type,
            "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
            "link": "/challenges",
        })

    # 3. My challenges that just completed (last 7 days)
    my_completed = (
        db.query(Challenge)
        .filter(
            Challenge.status == "completed",
            Challenge.updated_at >= since_7d,
            or_(
                Challenge.challenger_id == current.id,
                Challenge.opponent_id == current.id,
            ),
        )
        .all()
    )
    for ch in my_completed:
        ts = ch.updated_at
        notifications.append({
            "type": "challenge_completed",
            "id": f"ch_done_{ch.id}",
            "challenge_id": ch.id,
            "challenger": challenge_user_brief(ch.challenger),
            "opponent": challenge_user_brief(ch.opponent),
            "winner": challenge_user_brief(ch.winner) if ch.winner else None,
            "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
            "link": "/challenges",
        })

    if friend_ids:
        friend_id_list = list(friend_ids)

        # 4. Friend PRs in the last 7 days
        friend_prs = (
            db.query(UserOneRepMax)
            .filter(
                UserOneRepMax.user_id.in_(friend_id_list),
                UserOneRepMax.updated_at >= since_7d,
                UserOneRepMax.weight_kg > 0,
            )
            .order_by(UserOneRepMax.updated_at.desc())
            .limit(20)
            .all()
        )
        pr_cache: dict[int, dict] = {}
        pr_obj_cache: dict[int, User] = {}
        for pr in friend_prs:
            if pr.user_id not in pr_cache:
                u = db.query(User).filter(User.id == pr.user_id).first()
                if u:
                    pr_cache[pr.user_id] = public_user_dict(u)
                    pr_obj_cache[pr.user_id] = u
            user_data = pr_cache.get(pr.user_id)
            u_obj = pr_obj_cache.get(pr.user_id)
            if not user_data or not u_obj:
                continue
            level = None
            if u_obj.weight and u_obj.gender:
                level = classify_lift(pr.exercise_name, pr.weight_kg, u_obj.weight, u_obj.gender)
            ts = pr.updated_at
            notifications.append({
                "type": "friend_pr",
                "id": f"pr_{pr.user_id}_{pr.exercise_name}",
                "user": user_data,
                "exercise_name": pr.exercise_name,
                "weight_kg": pr.weight_kg,
                "level": level,
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "link": f"/u/{user_data['username']}",
            })

        # 5. Muscle achievements by friends (last 7 days)
        achievements = (
            db.query(MuscleAchievement)
            .filter(
                MuscleAchievement.user_id.in_(friend_id_list),
                MuscleAchievement.achieved_at >= since_7d,
            )
            .order_by(MuscleAchievement.achieved_at.desc())
            .limit(15)
            .all()
        )
        ach_cache: dict[int, dict] = {}
        for ach in achievements:
            if ach.user_id not in ach_cache:
                u = db.query(User).filter(User.id == ach.user_id).first()
                if u:
                    ach_cache[ach.user_id] = public_user_dict(u)
            user_data = ach_cache.get(ach.user_id)
            if not user_data:
                continue
            ts = ach.achieved_at
            notifications.append({
                "type": "muscle_achievement",
                "id": f"ach_{ach.id}",
                "user": user_data,
                "muscle_slug": ach.muscle_slug,
                "old_level": ach.old_level,
                "new_level": ach.new_level,
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "link": f"/u/{user_data['username']}",
            })

    # 6. Pending (unreviewed) reports — admin only
    if current.role == "admin":
        pending_reports = (
            db.query(Report)
            .filter(Report.reviewed == False)  # noqa: E712
            .order_by(Report.created_at.desc())
            .all()
        )
        for rep in pending_reports:
            ts = rep.created_at
            notifications.append({
                "type": "report",
                "id": f"rep_{rep.id}",
                "report_id": rep.id,
                "reporter_username": rep.reporter.username if rep.reporter else "?",
                "target_type": rep.target_type,
                "target_id": rep.target_id,
                "target_name": rep.target_name,
                "reason": rep.reason,
                "timestamp": ts.isoformat() if ts else now_naive.isoformat(),
                "link": (
                    f"/mealplans?open={rep.target_id}"
                    if rep.target_type == "meal"
                    else f"/workouts?open={rep.target_id}"
                ),
            })

    notifications.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"count": len(notifications), "notifications": notifications}
