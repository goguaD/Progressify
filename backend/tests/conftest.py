import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.database import Base, get_db
from app.models import User
from app.services.auth_service import create_access_token, hash_password

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def app():
    application = create_app()
    application.dependency_overrides[get_db] = _override_get_db
    return application


@pytest.fixture()
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db() -> Session:
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def make_user(
    db: Session,
    *,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123",
    gender: str = "male",
    role: str = "user",
    goal: str | None = None,
) -> User:
    user = User(
        username=username,
        firstname=username.capitalize(),
        lastname="User",
        email=email,
        password_hash=hash_password(password),
        gender=gender,
        role=role,
        goal=goal,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}
