import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime


USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
GENDERS = {"male", "female"}


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    firstname: str
    lastname: str
    middlename: Optional[str] = None
    email: EmailStr
    password: str
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = None
    gender: str

    @field_validator("username")
    @classmethod
    def _username_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not USERNAME_RE.match(v):
            raise ValueError(
                "Username must be 3-20 chars, lowercase letters, digits, or underscores."
            )
        return v

    @field_validator("gender")
    @classmethod
    def _gender_choice(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in GENDERS:
            raise ValueError("Gender must be 'male' or 'female'.")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    middlename: Optional[str]
    email: str
    weight: Optional[float]
    height: Optional[float]
    goal: Optional[str]
    gender: Optional[str]
    avatar_url: Optional[str]
    role: str
    created_at: Optional[datetime]
    last_seen: Optional[datetime]

    model_config = {"from_attributes": True}


class AdminUserOut(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    middlename: Optional[str]
    email: str
    password_hash: str
    weight: Optional[float]
    height: Optional[float]
    goal: Optional[str]
    gender: Optional[str]
    avatar_url: Optional[str]
    role: str
    created_at: Optional[datetime]
    last_seen: Optional[datetime]

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ─── Friends ──────────────────────────────────────────────────────────────────

FriendshipState = Literal["none", "pending_outgoing", "pending_incoming", "friends", "self"]


class PublicUser(BaseModel):
    """Lightweight public profile (no sensitive fields)."""
    id: int
    username: str
    firstname: str
    lastname: str
    goal: Optional[str]
    weight: Optional[float]
    height: Optional[float]
    gender: Optional[str]
    avatar_url: Optional[str]
    role: str
    last_seen: Optional[datetime]
    is_online: bool

    model_config = {"from_attributes": True}


class FriendCard(PublicUser):
    """Friend list entry — includes a placeholder activity blurb until we
    have real workout/meal-plan data wired up."""
    last_activity: Optional[str] = None
    current_workout: Optional[str] = None
    current_meal_plan: Optional[str] = None


class FriendRequestOut(BaseModel):
    id: int
    requester: PublicUser
    addressee: PublicUser
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ProfileView(PublicUser):
    """Profile shown when clicking on a user. Includes friendship state
    relative to the current viewer plus stats for the profile header."""
    relationship: FriendshipState
    pending_request_id: Optional[int] = None
    friend_count: int = 0
    current_workout: Optional[str] = None
    current_meal_plan: Optional[str] = None
    last_workout_text: Optional[str] = None


class FriendRequestCreate(BaseModel):
    username: str
