from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.repositories.user_repo import UserRepository
from app.schemas import Token, UserCreate, UserLogin
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> dict:
    repo = UserRepository(db)
    from fastapi import HTTPException

    if repo.get_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if repo.get_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=user_data.username,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        middlename=user_data.middlename,
        email=user_data.email,
        password_hash=auth_service.hash_password(user_data.password),
        weight=user_data.weight,
        height=user_data.height,
        age=user_data.age,
        goal=user_data.goal,
        gender=user_data.gender,
        role="user",
        last_seen=datetime.now(UTC),
        is_online=True,
    )
    user = repo.create(user)
    token = auth_service.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> dict:
    from fastapi import HTTPException

    repo = UserRepository(db)
    user = repo.get_by_email(credentials.email)
    if not user or not auth_service.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_seen = datetime.now(UTC)
    user.is_online = True
    repo.save()
    repo.refresh(user)

    token = auth_service.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    current.is_online = False
    db.commit()
    return {"ok": True}
