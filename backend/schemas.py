from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    firstname: str
    lastname: str
    middlename: Optional[str] = None
    email: EmailStr
    password: str
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    firstname: str
    lastname: str
    middlename: Optional[str]
    email: str
    weight: Optional[float]
    height: Optional[float]
    goal: Optional[str]
    role: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AdminUserOut(BaseModel):
    id: int
    firstname: str
    lastname: str
    middlename: Optional[str]
    email: str
    password_hash: str
    weight: Optional[float]
    height: Optional[float]
    goal: Optional[str]
    role: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
