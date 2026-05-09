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
from app.schemas import AdminUserOut, ProfileView, PublicUser, UserOut
from app.services.friend_service import friendship_state
from app.services.user_service import (
    placeholder_activity,
    public_user_dict,
)

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

    base = public_user_dict(user)
    base["relationship"] = state
    base["pending_request_id"] = req_id
    base["friend_count"] = len(friend_repo.accepted_friend_ids(user.id))
    base["current_workout"] = activity["current_workout"]
    base["current_meal_plan"] = activity["current_meal_plan"]
    base["last_workout_text"] = activity["last_activity"]
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
