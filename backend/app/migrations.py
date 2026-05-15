from sqlalchemy import text

from app.database import engine


def ensure_users_columns() -> None:
    """Lightweight forward-only migration for SQLite.

    Adds new columns that were introduced after the DB was first created,
    so users don't have to delete progressify.db on every schema bump.
    """
    expected: dict[str, str] = {
        "username": "VARCHAR",
        "last_seen": "DATETIME",
        "is_online": "BOOLEAN NOT NULL DEFAULT 0",
        "gender": "VARCHAR",
        "avatar_url": "VARCHAR",
    }
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing = {r[1] for r in rows}
        for name, decl in expected.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {decl}"))


def ensure_meals_columns() -> None:
    """Adds missing columns to the meals table and creates meal_views table."""
    with engine.begin() as conn:
        try:
            rows = conn.execute(text("PRAGMA table_info(meals)")).fetchall()
        except Exception:
            return
        existing = {r[1] for r in rows}
        new_cols: dict[str, str] = {
            "name_ka": "VARCHAR",
            "description_ka": "TEXT",
        }
        for name, decl in new_cols.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE meals ADD COLUMN {name} {decl}"))

        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS meal_views ("
                "id INTEGER PRIMARY KEY, "
                "meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE, "
                "user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE(meal_id, user_id))"
            )
        )


def ensure_challenges_columns() -> None:
    """Adds missing columns to the challenges table for forward-migration."""
    expected: dict[str, str] = {
        "deadline_notified": "BOOLEAN NOT NULL DEFAULT 0",
        "muscle_group": "VARCHAR",
        "endurance_mode": "VARCHAR",
        "endurance_speed": "FLOAT",
        "endurance_gradient": "FLOAT",
        "target_weight_kg": "FLOAT",
    }
    with engine.begin() as conn:
        try:
            rows = conn.execute(text("PRAGMA table_info(challenges)")).fetchall()
        except Exception:
            return
        existing = {r[1] for r in rows}
        for name, decl in expected.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE challenges ADD COLUMN {name} {decl}"))
