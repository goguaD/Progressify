from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Friendship, User
from app.repositories.friend_repo import FriendRepository
from app.repositories.user_repo import UserRepository
from app.schemas import FriendCard, FriendRequestCreate, FriendRequestOut
from app.services.user_service import placeholder_activity, public_user_dict

router = APIRouter(tags=["friends"])


@router.get("/friends", response_model=list[FriendCard])
def list_friends(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    friend_repo = FriendRepository(db)
    user_repo = UserRepository(db)

    friend_ids = friend_repo.accepted_friend_ids(current.id)
    if not friend_ids:
        return []

    friends = [user_repo.get_by_id(fid) for fid in friend_ids]
    cards: list[dict] = []
    for u in friends:
        if u is None:
            continue
        card = public_user_dict(u)
        card.update(placeholder_activity(u))
        cards.append(card)

    cards.sort(key=lambda c: (not c["is_online"], c["username"]))
    return cards


@router.get("/friends/requests", response_model=list[FriendRequestOut])
def list_pending_requests(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    repo = FriendRepository(db)
    rows = repo.pending_for_user(current.id)
    return [
        {
            "id": r.id,
            "requester": public_user_dict(r.requester),
            "addressee": public_user_dict(r.addressee),
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.post("/friends/request", status_code=201)
def send_friend_request(
    body: FriendRequestCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)

    target = user_repo.get_by_username(body.username.strip())
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current.id:
        raise HTTPException(status_code=400, detail="You can't add yourself.")
    if target.role == "admin" and current.role != "admin":
        raise HTTPException(status_code=404, detail="User not found")

    existing = friend_repo.find_between(current.id, target.id)
    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends.")
        if existing.status == "pending" and existing.requester_id == current.id:
            raise HTTPException(status_code=400, detail="Request already sent.")
        if existing.status == "pending" and existing.addressee_id == current.id:
            existing.status = "accepted"
            friend_repo.save()
            return {"ok": True, "auto_accepted": True}

    fr = Friendship(
        requester_id=current.id,
        addressee_id=target.id,
        status="pending",
    )
    friend_repo.create(fr)
    return {"ok": True}


@router.post("/friends/accept/{request_id}")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = FriendRepository(db)
    row = repo.get_by_id(request_id)
    if not row or row.addressee_id != current.id or row.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found")
    row.status = "accepted"
    repo.save()
    return {"ok": True}


@router.post("/friends/decline/{request_id}")
def decline_request(
    request_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = FriendRepository(db)
    row = repo.get_by_id(request_id)
    if not row or row.addressee_id != current.id or row.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found")
    repo.delete(row)
    return {"ok": True}


@router.delete("/friends/{user_id}")
def remove_friend(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = FriendRepository(db)
    row = repo.find_accepted_between(current.id, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Friendship not found")
    repo.delete(row)
    return {"ok": True}
