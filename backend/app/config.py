from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SQLALCHEMY_DATABASE_URL = "sqlite:///./progressify.db"

SECRET_KEY = "progressify-dev-secret-key-change-before-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

ONLINE_WINDOW = timedelta(seconds=90)

STATIC_DIR = BASE_DIR / "static"
AVATAR_DIR = STATIC_DIR / "avatars"

ALLOWED_AVATAR_TYPES: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 MB

CORS_ORIGINS: list[str] = ["http://localhost:5173"]
