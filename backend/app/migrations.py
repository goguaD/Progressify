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


def ensure_workouts_tables() -> None:
    """Creates the workout_plans, workout_days, and exercises tables if missing."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS workout_plans ("
                "id INTEGER PRIMARY KEY, "
                "name VARCHAR NOT NULL, "
                "name_ka VARCHAR, "
                "description TEXT NOT NULL, "
                "description_ka TEXT, "
                "image_url VARCHAR, "
                "days_per_week INTEGER NOT NULL, "
                "split_type VARCHAR NOT NULL, "
                "level VARCHAR NOT NULL DEFAULT 'intermediate', "
                "views INTEGER NOT NULL DEFAULT 0, "
                "is_default BOOLEAN NOT NULL DEFAULT 0, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS workout_days ("
                "id INTEGER PRIMARY KEY, "
                "plan_id INTEGER NOT NULL REFERENCES workout_plans(id) ON DELETE CASCADE, "
                "day_number INTEGER NOT NULL, "
                "name VARCHAR NOT NULL, "
                "name_ka VARCHAR, "
                "focus VARCHAR)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS exercises ("
                "id INTEGER PRIMARY KEY, "
                "day_id INTEGER NOT NULL REFERENCES workout_days(id) ON DELETE CASCADE, "
                "order_index INTEGER NOT NULL DEFAULT 0, "
                "name VARCHAR NOT NULL, "
                "name_ka VARCHAR, "
                "description TEXT NOT NULL, "
                "description_ka TEXT, "
                "image_url VARCHAR, "
                "sets INTEGER NOT NULL DEFAULT 3, "
                "rep_low INTEGER NOT NULL DEFAULT 8, "
                "rep_high INTEGER NOT NULL DEFAULT 12, "
                "rest_seconds INTEGER NOT NULL DEFAULT 90, "
                "primary_purpose VARCHAR NOT NULL DEFAULT 'hypertrophy', "
                "muscle_group VARCHAR NOT NULL DEFAULT 'general')"
            )
        )


def ensure_workouts_extra_tables() -> None:
    """Adds rating/view tables and rating columns to workout_plans."""
    with engine.begin() as conn:
        # Add rating columns to workout_plans if missing
        try:
            rows = conn.execute(
                text("PRAGMA table_info(workout_plans)"),
            ).fetchall()
        except Exception:
            return
        existing = {r[1] for r in rows}
        new_cols: dict[str, str] = {
            "rating_sum": "FLOAT NOT NULL DEFAULT 0.0",
            "rating_count": "INTEGER NOT NULL DEFAULT 0",
        }
        for name, decl in new_cols.items():
            if name not in existing:
                conn.execute(
                    text(f"ALTER TABLE workout_plans ADD COLUMN {name} {decl}"),
                )

        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS workout_plan_ratings ("
                "id INTEGER PRIMARY KEY, "
                "plan_id INTEGER NOT NULL "
                "REFERENCES workout_plans(id) ON DELETE CASCADE, "
                "user_id INTEGER NOT NULL "
                "REFERENCES users(id) ON DELETE CASCADE, "
                "score FLOAT NOT NULL, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE(plan_id, user_id))"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS workout_plan_views ("
                "id INTEGER PRIMARY KEY, "
                "plan_id INTEGER NOT NULL "
                "REFERENCES workout_plans(id) ON DELETE CASCADE, "
                "user_id INTEGER NOT NULL "
                "REFERENCES users(id) ON DELETE CASCADE, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE(plan_id, user_id))"
            )
        )


def ensure_workouts_user_columns() -> None:
    """Adds columns used for user-submitted workout plans."""
    with engine.begin() as conn:
        wp_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(workout_plans)"))
        }
        if "added_by" not in wp_cols:
            conn.execute(
                text(
                    "ALTER TABLE workout_plans "
                    "ADD COLUMN added_by INTEGER REFERENCES users(id)",
                ),
            )

        ex_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(exercises)"))
        }
        if "muscle_targets" not in ex_cols:
            conn.execute(
                text("ALTER TABLE exercises ADD COLUMN muscle_targets TEXT"),
            )


def ensure_user_active_workout_tables() -> None:
    """Creates the tables that track a user's active plan and 1RMs."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS user_active_workout_plans ("
                "user_id INTEGER PRIMARY KEY "
                "REFERENCES users(id) ON DELETE CASCADE, "
                "plan_id INTEGER NOT NULL "
                "REFERENCES workout_plans(id) ON DELETE CASCADE, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS user_one_rep_max ("
                "id INTEGER PRIMARY KEY, "
                "user_id INTEGER NOT NULL "
                "REFERENCES users(id) ON DELETE CASCADE, "
                "exercise_name VARCHAR NOT NULL, "
                "weight_kg FLOAT NOT NULL, "
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "UNIQUE(user_id, exercise_name))"
            )
        )


def ensure_muscle_achievements_table() -> None:
    """Creates the muscle_achievements table if it doesn't exist."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS muscle_achievements ("
                "id INTEGER PRIMARY KEY, "
                "user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, "
                "muscle_slug VARCHAR NOT NULL, "
                "old_level VARCHAR, "
                "new_level VARCHAR NOT NULL, "
                "achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
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
