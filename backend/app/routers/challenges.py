from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Challenge, User
from app.repositories.challenge_repo import ChallengeRepository
from app.repositories.friend_repo import FriendRepository
from app.repositories.user_repo import UserRepository
from app.schemas import ChallengeCreate, ChallengeOut, ChallengeResultSubmit, H2HScore
from app.services.challenge_service import (
    challenge_out,
    compute_h2h,
    resolve_challenge,
    safe_deadline,
)

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.post("", status_code=201)
def create_challenge(
    body: ChallengeCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)
    challenge_repo = ChallengeRepository(db)

    opponent = user_repo.get_by_username(body.opponent_username.strip())
    if not opponent:
        raise HTTPException(status_code=404, detail="User not found")
    if opponent.id == current.id:
        raise HTTPException(status_code=400, detail="You can't challenge yourself.")

    friend_ids = friend_repo.accepted_friend_ids(current.id)
    if opponent.id not in friend_ids:
        raise HTTPException(status_code=400, detail="You can only challenge friends.")

    dl: datetime | None = None
    if body.challenge_type in ("strength", "endurance"):
        if not body.deadline:
            raise HTTPException(
                status_code=400,
                detail="Deadline is required for this challenge type.",
            )
        dl = body.deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=UTC)
        if dl <= datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Deadline must be in the future.")

    if body.challenge_type == "strength" and not body.muscle_group:
        raise HTTPException(
            status_code=400,
            detail="Muscle group is required for strength challenges.",
        )

    if body.challenge_type == "endurance":
        if body.endurance_mode not in ("treadmill", "stairs"):
            raise HTTPException(
                status_code=400,
                detail="Endurance mode must be 'treadmill' or 'stairs'.",
            )
        if not body.endurance_speed or body.endurance_speed <= 0:
            raise HTTPException(status_code=400, detail="Speed is required.")
        if (
            body.endurance_mode == "treadmill"
            and body.endurance_gradient is not None
            and body.endurance_gradient < 0
        ):
            raise HTTPException(status_code=400, detail="Gradient cannot be negative.")

    if body.challenge_type == "target_weight" and (
        not body.target_weight_kg or body.target_weight_kg <= 0
    ):
        raise HTTPException(status_code=400, detail="Target weight is required.")

    ch = Challenge(
        challenger_id=current.id,
        opponent_id=opponent.id,
        challenge_type=body.challenge_type,
        message=body.message,
        deadline=dl,
        muscle_group=(body.muscle_group if body.challenge_type == "strength" else None),
        endurance_mode=(body.endurance_mode if body.challenge_type == "endurance" else None),
        endurance_speed=(body.endurance_speed if body.challenge_type == "endurance" else None),
        endurance_gradient=(
            body.endurance_gradient
            if body.challenge_type == "endurance" and body.endurance_mode == "treadmill"
            else None
        ),
        target_weight_kg=(
            body.target_weight_kg if body.challenge_type == "target_weight" else None
        ),
    )
    ch = challenge_repo.create(ch)
    return challenge_out(ch, current.id)


@router.get("", response_model=list[ChallengeOut])
def list_challenges(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[dict]:
    repo = ChallengeRepository(db)
    challenges = repo.list_for_user(current.id, status=status)

    now = datetime.now(UTC)
    result: list[dict] = []
    for ch in challenges:
        dl = safe_deadline(ch)
        if ch.status == "accepted" and dl is not None and now >= dl:
            resolve_challenge(ch, repo)
        result.append(challenge_out(ch, current.id))
    return result


@router.get("/h2h/{user_id}", response_model=H2HScore)
def head_to_head(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    user_repo = UserRepository(db)
    challenge_repo = ChallengeRepository(db)

    opponent = user_repo.get_by_id(user_id)
    if not opponent:
        raise HTTPException(status_code=404, detail="User not found")

    scores = compute_h2h(challenge_repo, current.id, user_id)
    return {
        "opponent_id": user_id,
        "opponent_username": opponent.username,
        **scores,
    }


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = ChallengeRepository(db)
    ch = repo.get_by_id(challenge_id)
    if not ch or (ch.challenger_id != current.id and ch.opponent_id != current.id):
        raise HTTPException(status_code=404, detail="Challenge not found")

    dl = safe_deadline(ch)
    if ch.status == "accepted" and dl is not None and datetime.now(UTC) >= dl:
        resolve_challenge(ch, repo)

    return challenge_out(ch, current.id)


@router.post("/{challenge_id}/accept")
def accept_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = ChallengeRepository(db)
    ch = repo.get_by_id(challenge_id)
    if not ch or ch.opponent_id != current.id or ch.status != "pending":
        raise HTTPException(status_code=404, detail="Challenge not found")
    ch.status = "accepted"
    repo.save()
    return {"ok": True}


@router.post("/{challenge_id}/decline")
def decline_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = ChallengeRepository(db)
    ch = repo.get_by_id(challenge_id)
    if not ch or ch.opponent_id != current.id or ch.status != "pending":
        raise HTTPException(status_code=404, detail="Challenge not found")
    ch.status = "declined"
    repo.save()
    return {"ok": True}


@router.post("/{challenge_id}/submit")
def submit_result(
    challenge_id: int,
    body: ChallengeResultSubmit,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    repo = ChallengeRepository(db)
    ch = repo.get_by_id(challenge_id)
    if not ch or (ch.challenger_id != current.id and ch.opponent_id != current.id):
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.status != "accepted":
        raise HTTPException(status_code=400, detail="Challenge is not active.")

    dl = safe_deadline(ch)
    if dl is not None and datetime.now(UTC) >= dl:
        resolve_challenge(ch, repo)
        raise HTTPException(status_code=400, detail="Deadline has passed.")

    if body.value < 0:
        raise HTTPException(status_code=400, detail="Value must be non-negative.")

    now = datetime.now(UTC)
    val_str = str(body.value)

    if ch.challenger_id == current.id:
        if ch.challenger_submitted_at:
            raise HTTPException(status_code=400, detail="Already submitted.")
        ch.challenger_result = val_str
        ch.challenger_submitted_at = now
    else:
        if ch.opponent_submitted_at:
            raise HTTPException(status_code=400, detail="Already submitted.")
        ch.opponent_result = val_str
        ch.opponent_submitted_at = now

    repo.save()
    repo.refresh(ch)

    should_resolve = ch.challenge_type == "target_weight" or (
        ch.challenger_submitted_at and ch.opponent_submitted_at
    )
    if should_resolve:
        resolve_challenge(ch, repo)

    return challenge_out(ch, current.id)
