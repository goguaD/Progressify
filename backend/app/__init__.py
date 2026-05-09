from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AVATAR_DIR, CORS_ORIGINS, STATIC_DIR
from app.database import SessionLocal, engine
from app.migrations import ensure_challenges_columns, ensure_users_columns
from app.models import Base, User
from app.routers import auth, challenges, friends, users
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


def create_app() -> FastAPI:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    ensure_users_columns()
    ensure_challenges_columns()
    _seed_admin()

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

    @app.get("/")
    def root() -> dict:
        return {"message": "Progressify API is running"}

    return app
