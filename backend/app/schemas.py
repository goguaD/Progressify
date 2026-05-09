import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
GENDERS = {"male", "female"}

CHALLENGE_TYPES = {"strength", "endurance", "target_weight"}
ENDURANCE_MODES = {"treadmill", "stairs"}


# ── Auth ──────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    username: str
    firstname: str
    lastname: str
    middlename: str | None = None
    email: EmailStr
    password: str
    weight: float | None = None
    height: float | None = None
    goal: str | None = None
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
    middlename: str | None
    email: str
    weight: float | None
    height: float | None
    goal: str | None
    gender: str | None
    avatar_url: str | None
    role: str
    created_at: datetime | None
    last_seen: datetime | None

    model_config = {"from_attributes": True}


class AdminUserOut(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    middlename: str | None
    email: str
    password_hash: str
    weight: float | None
    height: float | None
    goal: str | None
    gender: str | None
    avatar_url: str | None
    role: str
    created_at: datetime | None
    last_seen: datetime | None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Friends ───────────────────────────────────────────────────────────────────

FriendshipState = Literal["none", "pending_outgoing", "pending_incoming", "friends", "self"]


class PublicUser(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    goal: str | None
    weight: float | None
    height: float | None
    gender: str | None
    avatar_url: str | None
    role: str
    last_seen: datetime | None
    is_online: bool

    model_config = {"from_attributes": True}


class FriendCard(PublicUser):
    last_activity: str | None = None
    current_workout: str | None = None
    current_meal_plan: str | None = None


class FriendRequestOut(BaseModel):
    id: int
    requester: PublicUser
    addressee: PublicUser
    created_at: datetime | None

    model_config = {"from_attributes": True}


class ProfileView(PublicUser):
    relationship: FriendshipState
    pending_request_id: int | None = None
    friend_count: int = 0
    current_workout: str | None = None
    current_meal_plan: str | None = None
    last_workout_text: str | None = None


class FriendRequestCreate(BaseModel):
    username: str


# ── Challenges ────────────────────────────────────────────────────────────────


class ChallengeCreate(BaseModel):
    opponent_username: str
    challenge_type: str
    deadline: datetime | None = None
    message: str | None = None

    muscle_group: str | None = None

    endurance_mode: str | None = None
    endurance_speed: float | None = None
    endurance_gradient: float | None = None

    target_weight_kg: float | None = None

    @field_validator("challenge_type")
    @classmethod
    def _valid_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in CHALLENGE_TYPES:
            raise ValueError(f"challenge_type must be one of: {', '.join(sorted(CHALLENGE_TYPES))}")
        return v


class ChallengeResultSubmit(BaseModel):
    value: float


class ChallengeUserBrief(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    avatar_url: str | None
    is_online: bool

    model_config = {"from_attributes": True}


class ChallengeOut(BaseModel):
    id: int
    challenger: ChallengeUserBrief
    opponent: ChallengeUserBrief
    challenge_type: str
    message: str | None
    deadline: datetime | None
    status: str
    created_at: datetime | None

    muscle_group: str | None = None
    endurance_mode: str | None = None
    endurance_speed: float | None = None
    endurance_gradient: float | None = None
    target_weight_kg: float | None = None

    my_result: float | None = None
    their_result: float | None = None
    my_submitted: bool = False
    their_submitted: bool = False
    winner: ChallengeUserBrief | None = None

    deadline_soon: bool = False

    model_config = {"from_attributes": True}


class H2HScore(BaseModel):
    opponent_id: int
    opponent_username: str
    wins: int
    losses: int
    draws: int
