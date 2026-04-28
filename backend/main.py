import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_, and_, text
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import SessionLocal, engine, get_db

# ── Static / uploads ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
AVATAR_DIR = STATIC_DIR / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_AVATAR_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 MB

# ── Online threshold ─────────────────────────────────────────────────────────
# A user is considered "online" if they explicitly intend to be (is_online flag)
# AND their heartbeat is fresh (last_seen within this window). This means
# logged-out users go offline immediately, but closed-tab users still drift
# offline after ONLINE_WINDOW.
ONLINE_WINDOW = timedelta(seconds=90)


models.Base.metadata.create_all(bind=engine)


def _ensure_users_columns():
    """Lightweight forward-only migration for SQLite. Adds new columns that
    were introduced after the DB was first created, so users don't have to
    delete progressify.db on every schema bump."""
    expected = {
        "username":    "VARCHAR",
        "last_seen":   "DATETIME",
        "is_online":   "BOOLEAN NOT NULL DEFAULT 0",
        "gender":      "VARCHAR",
        "avatar_url":  "VARCHAR",
    }
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing = {r[1] for r in rows}
        for name, decl in expected.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {decl}"))


_ensure_users_columns()

app = FastAPI(title="Progressify API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(
            models.User.email == "admin@progressify.ge"
        ).first()
        if not existing:
            admin = models.User(
                username="admin",
                firstname="Admin",
                lastname="Progressify",
                middlename=None,
                email="admin@progressify.ge",
                password_hash=auth.hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created: admin@progressify.ge / admin123")
        else:
            print("ℹ️  Admin user already exists.")
    finally:
        db.close()


seed_admin()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _is_online(user: models.User) -> bool:
    if not user.is_online or not user.last_seen:
        return False
    last = user.last_seen
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last) <= ONLINE_WINDOW


def _public_user(user: models.User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "goal": user.goal,
        "weight": user.weight,
        "height": user.height,
        "gender": user.gender,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "last_seen": user.last_seen,
        "is_online": _is_online(user),
    }


def _placeholder_activity(user: models.User) -> dict:
    """Until workouts/mealplans tables exist, fabricate a friendly blurb so
    the friends feed has something to show."""
    workouts_by_goal = {
        "muscle_gain": "Push Day · Chest & Triceps",
        "weight_loss": "HIIT Cardio · 30 min",
        "maintain": "Full Body · Maintenance",
        "endurance": "Long Run · 8 km",
        "flexibility": "Yoga Flow · 45 min",
    }
    meals_by_goal = {
        "muscle_gain": "High-Protein Bulk",
        "weight_loss": "Calorie Deficit Plan",
        "maintain": "Balanced Macros",
        "endurance": "Carb-Forward Plan",
        "flexibility": "Mediterranean Plan",
    }
    workout = workouts_by_goal.get(user.goal or "", "No workout yet")
    meal = meals_by_goal.get(user.goal or "", "No meal plan yet")

    if user.last_seen:
        last = user.last_seen
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - last
        if user.is_online and delta < timedelta(minutes=5):
            activity = "Active right now"
        elif delta < timedelta(hours=1):
            mins = int(delta.total_seconds() // 60)
            activity = f"Last seen {mins} min ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() // 3600)
            activity = f"Last seen {hours}h ago"
        else:
            days = delta.days
            activity = f"Last seen {days}d ago"
    else:
        activity = "Hasn't logged in yet"

    return {
        "current_workout": workout,
        "current_meal_plan": meal,
        "last_activity": activity,
    }


def _accepted_friend_ids(db: Session, user_id: int) -> set[int]:
    rows = (
        db.query(models.Friendship)
        .filter(
            models.Friendship.status == "accepted",
            or_(
                models.Friendship.requester_id == user_id,
                models.Friendship.addressee_id == user_id,
            ),
        )
        .all()
    )
    ids: set[int] = set()
    for r in rows:
        ids.add(r.requester_id if r.requester_id != user_id else r.addressee_id)
    return ids


def _friendship_state(
    db: Session, viewer_id: int, target_id: int
) -> tuple[schemas.FriendshipState, Optional[int]]:
    if viewer_id == target_id:
        return "self", None
    row = (
        db.query(models.Friendship)
        .filter(
            or_(
                and_(
                    models.Friendship.requester_id == viewer_id,
                    models.Friendship.addressee_id == target_id,
                ),
                and_(
                    models.Friendship.requester_id == target_id,
                    models.Friendship.addressee_id == viewer_id,
                ),
            )
        )
        .first()
    )
    if not row:
        return "none", None
    if row.status == "accepted":
        return "friends", row.id
    if row.status == "pending":
        if row.requester_id == viewer_id:
            return "pending_outgoing", row.id
        return "pending_incoming", row.id
    return "none", None


# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=user_data.username,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        middlename=user_data.middlename,
        email=user_data.email,
        password_hash=auth.hash_password(user_data.password),
        weight=user_data.weight,
        height=user_data.height,
        goal=user_data.goal,
        gender=user_data.gender,
        role="user",
        last_seen=datetime.now(timezone.utc),
        is_online=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == credentials.email
    ).first()
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_seen = datetime.now(timezone.utc)
    user.is_online = True
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/logout")
def logout(
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """Explicitly mark this user offline. Cheap to call; safe to fire-and-forget
    from the client during logout."""
    current.is_online = False
    db.commit()
    return {"ok": True}


@app.get("/me", response_model=schemas.UserOut)
def me(current: models.User = Depends(auth.get_current_user)):
    """Return current user. Used as a heartbeat — get_current_user
    automatically bumps last_seen."""
    return current


# ─── User search & profile ────────────────────────────────────────────────────

@app.get("/users/search", response_model=List[schemas.PublicUser])
def search_users(
    q: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    needle = q.strip().lower()
    if not needle:
        return []

    query = (
        db.query(models.User)
        .filter(models.User.username.ilike(f"%{needle}%"))
        .filter(models.User.id != current.id)
    )
    # Admins are invisible to non-admins (they can't be friended).
    if current.role != "admin":
        query = query.filter(models.User.role != "admin")

    rows = query.order_by(models.User.username.asc()).limit(15).all()
    return [_public_user(u) for u in rows]


@app.get("/users/by-username/{username}", response_model=schemas.ProfileView)
def get_profile(
    username: str,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    user = (
        db.query(models.User)
        .filter(models.User.username == username.lower())
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hide admin profiles from non-admin viewers (admin can still view themselves).
    if user.role == "admin" and current.role != "admin" and user.id != current.id:
        raise HTTPException(status_code=404, detail="User not found")

    state, req_id = _friendship_state(db, current.id, user.id)
    activity = _placeholder_activity(user)

    base = _public_user(user)
    base["relationship"] = state
    base["pending_request_id"] = req_id
    base["friend_count"] = len(_accepted_friend_ids(db, user.id))
    base["current_workout"] = activity["current_workout"]
    base["current_meal_plan"] = activity["current_meal_plan"]
    base["last_workout_text"] = activity["last_activity"]
    return base


# ─── Friends ──────────────────────────────────────────────────────────────────

@app.get("/friends", response_model=List[schemas.FriendCard])
def list_friends(
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    friend_ids = _accepted_friend_ids(db, current.id)
    if not friend_ids:
        return []
    friends = db.query(models.User).filter(models.User.id.in_(friend_ids)).all()

    cards: list[dict] = []
    for u in friends:
        card = _public_user(u)
        card.update(_placeholder_activity(u))
        cards.append(card)

    cards.sort(key=lambda c: (not c["is_online"], c["username"]))
    return cards


@app.get("/friends/requests", response_model=List[schemas.FriendRequestOut])
def list_pending_requests(
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    rows = (
        db.query(models.Friendship)
        .filter(
            models.Friendship.status == "pending",
            models.Friendship.addressee_id == current.id,
        )
        .order_by(models.Friendship.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "requester": _public_user(r.requester),
            "addressee": _public_user(r.addressee),
            "created_at": r.created_at,
        }
        for r in rows
    ]


@app.post("/friends/request", status_code=201)
def send_friend_request(
    body: schemas.FriendRequestCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    target = (
        db.query(models.User)
        .filter(models.User.username == body.username.strip().lower())
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current.id:
        raise HTTPException(status_code=400, detail="You can't add yourself.")
    if target.role == "admin" and current.role != "admin":
        # Admins are invisible to regular users; pretend they don't exist.
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(models.Friendship)
        .filter(
            or_(
                and_(
                    models.Friendship.requester_id == current.id,
                    models.Friendship.addressee_id == target.id,
                ),
                and_(
                    models.Friendship.requester_id == target.id,
                    models.Friendship.addressee_id == current.id,
                ),
            )
        )
        .first()
    )
    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends.")
        if existing.status == "pending" and existing.requester_id == current.id:
            raise HTTPException(status_code=400, detail="Request already sent.")
        if existing.status == "pending" and existing.addressee_id == current.id:
            # Auto-accept: they already sent us one.
            existing.status = "accepted"
            db.commit()
            return {"ok": True, "auto_accepted": True}

    fr = models.Friendship(
        requester_id=current.id,
        addressee_id=target.id,
        status="pending",
    )
    db.add(fr)
    db.commit()
    return {"ok": True}


@app.post("/friends/accept/{request_id}")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    row = db.query(models.Friendship).filter(models.Friendship.id == request_id).first()
    if not row or row.addressee_id != current.id or row.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found")
    row.status = "accepted"
    db.commit()
    return {"ok": True}


@app.post("/friends/decline/{request_id}")
def decline_request(
    request_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    row = db.query(models.Friendship).filter(models.Friendship.id == request_id).first()
    if not row or row.addressee_id != current.id or row.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


@app.delete("/friends/{user_id}")
def remove_friend(
    user_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    row = (
        db.query(models.Friendship)
        .filter(
            models.Friendship.status == "accepted",
            or_(
                and_(
                    models.Friendship.requester_id == current.id,
                    models.Friendship.addressee_id == user_id,
                ),
                and_(
                    models.Friendship.requester_id == user_id,
                    models.Friendship.addressee_id == current.id,
                ),
            ),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Friendship not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ─── Avatar upload ────────────────────────────────────────────────────────────

@app.post("/me/avatar", response_model=schemas.UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
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

    # Wipe any previous avatar to avoid stale files for this user.
    for old in AVATAR_DIR.glob(f"{current.id}.*"):
        try:
            old.unlink()
        except OSError:
            pass

    ext = ALLOWED_AVATAR_TYPES[file.content_type]
    # Cache-busting query param so the browser picks up new uploads instantly.
    cache_bust = uuid.uuid4().hex[:8]
    fname = f"{current.id}{ext}"
    out_path = AVATAR_DIR / fname
    with open(out_path, "wb") as f:
        f.write(contents)

    current.avatar_url = f"/static/avatars/{fname}?v={cache_bust}"
    db.commit()
    db.refresh(current)
    return current


@app.delete("/me/avatar", response_model=schemas.UserOut)
def delete_avatar(
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    for old in AVATAR_DIR.glob(f"{current.id}.*"):
        try:
            old.unlink()
        except OSError:
            pass
    current.avatar_url = None
    db.commit()
    db.refresh(current)
    return current


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.get("/admin/users", response_model=List[schemas.AdminUserOut])
def get_all_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin_user),
):
    return db.query(models.User).order_by(models.User.id.asc()).all()


@app.get("/")
def root():
    return {"message": "Progressify API is running"}
