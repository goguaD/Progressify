from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AVATAR_DIR, CORS_ORIGINS, MEAL_IMG_DIR, STATIC_DIR, WORKOUT_IMG_DIR
from app.database import SessionLocal, engine
from app.migrations import (
    ensure_challenges_columns,
    ensure_meals_columns,
    ensure_user_active_workout_tables,
    ensure_users_columns,
    ensure_workouts_extra_tables,
    ensure_workouts_tables,
    ensure_workouts_user_columns,
)
from app.models import Base, User
from app.routers import auth, challenges, friends, meals, users, workouts
from app.services import auth_service


def _seed_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@progressify.ge").first()
        if not existing:
            admin = User(
                username="admin",
                firstname="Admin",
                lastname="Progressify",
                middlename=None,
                email="admin@progressify.ge",
                password_hash=auth_service.hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def _seed_default_meals() -> None:
    from app.models import Meal
    from app.services.meal_service import DEFAULT_MEALS, GEORGIAN_TRANSLATIONS

    db = SessionLocal()
    try:
        active_names = {d["name"] for d in DEFAULT_MEALS}

        # Remove default meals no longer in the seed list
        db.query(Meal).filter(
            Meal.is_default == True,  # noqa: E712
            Meal.name.notin_(active_names),
        ).delete(synchronize_session=False)

        for data in DEFAULT_MEALS:
            ka = GEORGIAN_TRANSLATIONS.get(data["name"], {})
            full_data = {**data, **ka}
            existing = (
                db.query(Meal)
                .filter(Meal.name == full_data["name"], Meal.is_default == True)  # noqa: E712
                .first()
            )
            if existing:
                for key, val in full_data.items():
                    setattr(existing, key, val)
            else:
                db.add(Meal(**full_data, is_default=True))
        db.commit()
    finally:
        db.close()


def _seed_default_workout_plans() -> None:
    from app.models import WorkoutPlan
    from app.services.workout_service import DEFAULT_PLANS, build_plan_models

    db = SessionLocal()
    try:
        # Strategy: blow away all default plans and rebuild from spec. Cascade
        # handles days + exercises. Views on default plans aren't user data we
        # care about preserving across seed changes.
        existing_plans = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.is_default == True)  # noqa: E712
            .all()
        )
        existing_views = {p.name: p.views for p in existing_plans}
        for p in existing_plans:
            db.delete(p)
        db.flush()

        for spec in DEFAULT_PLANS:
            plan = build_plan_models(spec)
            prev_views = existing_views.get(spec["name"], 0)
            plan.views = prev_views  # type: ignore[assignment]
            db.add(plan)
        db.commit()
    finally:
        db.close()


def create_app() -> FastAPI:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    MEAL_IMG_DIR.mkdir(parents=True, exist_ok=True)
    WORKOUT_IMG_DIR.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    ensure_users_columns()
    ensure_challenges_columns()
    ensure_meals_columns()
    ensure_workouts_tables()
    ensure_workouts_extra_tables()
    ensure_workouts_user_columns()
    ensure_user_active_workout_tables()
    _seed_admin()
    _seed_default_meals()
    _seed_default_workout_plans()

    app = FastAPI(title="Progressify API", version="2.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(friends.router)
    app.include_router(challenges.router)
    app.include_router(meals.router)
    app.include_router(workouts.router)
    app.include_router(workouts.me_router)

    @app.get("/")
    def root() -> dict:
        return {"message": "Progressify API is running"}

    return app
