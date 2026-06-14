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
    age: int | None = None
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
    age: int | None
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
    age: int | None
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
    muscle_levels: dict[str, str] = {}
    active_workout: dict | None = None


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


# ── Meals ────────────────────────────────────────────────────────────────────

MEAL_GOALS = {"cut", "bulk", "maintain", "general", "cheat"}


class MealOut(BaseModel):
    id: int
    name: str
    name_ka: str | None = None
    description: str
    description_ka: str | None = None
    image_url: str | None
    goal: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float | None
    sugar: float | None
    views: int
    rating: float
    rating_count: int
    my_rating: float | None = None
    added_by_username: str | None = None
    is_default: bool
    created_at: datetime | None

    model_config = {"from_attributes": True}


class MealRateRequest(BaseModel):
    score: float

    @field_validator("score")
    @classmethod
    def _valid_score(cls, v: float) -> float:
        if v < 0 or v > 5:
            raise ValueError("Score must be between 0 and 5.")
        if (v * 2) != int(v * 2):
            raise ValueError("Score must be in 0.5 increments.")
        return v


# ── Workouts ─────────────────────────────────────────────────────────────────

WORKOUT_PURPOSES = {"strength", "hypertrophy", "endurance"}
WORKOUT_LEVELS = {"beginner", "intermediate", "advanced"}


class MuscleTarget(BaseModel):
    slug: str
    intensity: Literal["low", "medium", "high"]


class ExerciseOut(BaseModel):
    id: int
    order_index: int
    name: str
    name_ka: str | None = None
    description: str
    description_ka: str | None = None
    image_url: str | None
    sets: int
    rep_low: int
    rep_high: int
    rest_seconds: int
    primary_purpose: str
    muscle_group: str
    muscle_targets: list[MuscleTarget] = []
    unit_hint: str | None = None
    unit_hint_ka: str | None = None

    model_config = {"from_attributes": True}


class WorkoutDayOut(BaseModel):
    id: int
    day_number: int
    name: str
    name_ka: str | None = None
    focus: str | None = None
    exercises: list[ExerciseOut]

    model_config = {"from_attributes": True}


class WorkoutPlanOut(BaseModel):
    id: int
    name: str
    name_ka: str | None = None
    description: str
    description_ka: str | None = None
    image_url: str | None
    days_per_week: int
    split_type: str
    level: str
    views: int
    rating: float
    rating_count: int
    my_rating: float | None = None
    is_default: bool
    added_by_username: str | None = None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class WorkoutPlanDetail(WorkoutPlanOut):
    days: list[WorkoutDayOut]


class WorkoutRateRequest(BaseModel):
    score: float

    @field_validator("score")
    @classmethod
    def _valid_workout_score(cls, v: float) -> float:
        if v < 0 or v > 5:
            raise ValueError("Score must be between 0 and 5.")
        if (v * 2) != int(v * 2):
            raise ValueError("Score must be in 0.5 increments.")
        return v


# ── User active plan + 1RM ───────────────────────────────────────────────────

class OneRepMaxItem(BaseModel):
    exercise_name: str
    weight_kg: float

    @field_validator("weight_kg")
    @classmethod
    def _valid_weight(cls, v: float) -> float:
        if v < 0 or v > 1000:
            raise ValueError("weight_kg must be between 0 and 1000.")
        return v


class OneRepMaxOut(BaseModel):
    exercise_name: str
    weight_kg: float
    muscle_group: str | None = None
    level: str | None = None
    has_standard: bool = False
    unit_hint: str | None = None
    unit_hint_ka: str | None = None

    model_config = {"from_attributes": True}


class SetActivePlanRequest(BaseModel):
    plan_id: int
    lifts: list[OneRepMaxItem] = []


class UpdateLiftsRequest(BaseModel):
    lifts: list[OneRepMaxItem]


class ActivePlanOut(BaseModel):
    plan: WorkoutPlanDetail
    lifts: list[OneRepMaxOut]
    muscle_levels: dict[str, str]
    bodyweight_kg: float | None


# ── User-submitted workout plans ────────────────────────────────────────────

class ExerciseCreate(BaseModel):
    name: str
    name_ka: str | None = None
    description: str = ""
    description_ka: str | None = None
    sets: int = 3
    rep_low: int = 8
    rep_high: int = 12
    rest_seconds: int = 90
    primary_purpose: Literal["strength", "hypertrophy", "endurance"] = "hypertrophy"
    muscle_group: str = "general"
    muscle_targets: list[MuscleTarget] = []

    @field_validator("sets")
    @classmethod
    def _valid_sets(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError("sets must be between 1 and 20.")
        return v

    @field_validator("rep_low")
    @classmethod
    def _valid_rep_low(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("rep_low must be between 1 and 100.")
        return v

    @field_validator("rep_high")
    @classmethod
    def _valid_rep_high(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("rep_high must be between 1 and 100.")
        return v

    @field_validator("rest_seconds")
    @classmethod
    def _valid_rest(cls, v: int) -> int:
        if v < 0 or v > 1200:
            raise ValueError("rest_seconds must be between 0 and 1200.")
        return v


class DayCreate(BaseModel):
    day_number: int
    name: str
    name_ka: str | None = None
    focus: str | None = None
    exercises: list[ExerciseCreate]


class WorkoutPlanCreate(BaseModel):
    name: str
    name_ka: str | None = None
    description: str = ""
    description_ka: str | None = None
    days_per_week: int
    split_type: str = "custom"
    level: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    days: list[DayCreate]

    @field_validator("days_per_week")
    @classmethod
    def _valid_dpw(cls, v: int) -> int:
        if v < 1 or v > 7:
            raise ValueError("days_per_week must be between 1 and 7.")
        return v
