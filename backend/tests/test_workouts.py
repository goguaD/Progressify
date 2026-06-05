"""Integration tests for app.routers.workouts endpoints."""
from app.models import Exercise, WorkoutDay, WorkoutPlan
from tests.conftest import auth_headers, make_user


def _seed_plan(db, **overrides) -> WorkoutPlan:
    defaults = dict(
        name="API Test Plan",
        description="A plan for tests",
        days_per_week=3,
        split_type="ppl",
        level="intermediate",
        is_default=True,
        views=0,
        rating_sum=0.0,
        rating_count=0,
    )
    defaults.update(overrides)
    plan = WorkoutPlan(**defaults)
    for i in range(plan.days_per_week):
        day = WorkoutDay(
            day_number=i + 1,
            name=f"Day {i + 1}",
            focus="chest" if i == 0 else "back",
        )
        day.exercises.append(
            Exercise(
                order_index=0, name=f"Ex{i}", description="desc",
                sets=3, rep_low=8, rep_high=12, rest_seconds=90,
                primary_purpose="hypertrophy", muscle_group="chest",
            ),
        )
        plan.days.append(day)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


class TestListPlansAPI:
    def test_requires_auth(self, client):
        resp = client.get("/workouts")
        assert resp.status_code in {401, 403}

    def test_list_returns_seeded_plans(self, client, db):
        user = make_user(db)
        _seed_plan(db, name="A")
        _seed_plan(db, name="B")
        resp = client.get("/workouts", headers=auth_headers(user))
        assert resp.status_code == 200
        names = {p["name"] for p in resp.json()}
        assert "A" in names and "B" in names

    def test_filter_by_days_per_week(self, client, db):
        user = make_user(db)
        _seed_plan(db, name="Custom3", days_per_week=3)
        _seed_plan(db, name="Custom5", days_per_week=5)
        resp = client.get("/workouts?days_per_week=5", headers=auth_headers(user))
        names = {p["name"] for p in resp.json()}
        assert "Custom5" in names
        assert "Custom3" not in names

    def test_filter_by_level(self, client, db):
        user = make_user(db)
        _seed_plan(db, name="MyBeg", level="beginner")
        _seed_plan(db, name="MyAdv", level="advanced")
        resp = client.get("/workouts?level=beginner", headers=auth_headers(user))
        levels = {p["level"] for p in resp.json()}
        assert levels == {"beginner"}

    def test_pagination_caps(self, client, db):
        user = make_user(db)
        for i in range(8):
            _seed_plan(db, name=f"Plan{i}")
        resp = client.get("/workouts?limit=3", headers=auth_headers(user))
        assert len(resp.json()) == 3

    def test_invalid_days_per_week_rejected(self, client, db):
        user = make_user(db)
        resp = client.get("/workouts?days_per_week=0", headers=auth_headers(user))
        assert resp.status_code == 422
        resp = client.get("/workouts?days_per_week=8", headers=auth_headers(user))
        assert resp.status_code == 422

    def test_list_includes_rating_fields(self, client, db):
        user = make_user(db)
        _seed_plan(db, name="Rated", rating_sum=9.0, rating_count=2)
        resp = client.get("/workouts", headers=auth_headers(user))
        plan = next(p for p in resp.json() if p["name"] == "Rated")
        assert plan["rating"] == 4.5
        assert plan["rating_count"] == 2
        assert plan["my_rating"] is None


class TestGetPlanAPI:
    def test_returns_detail_with_days_and_exercises(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        resp = client.get(f"/workouts/{plan.id}", headers=auth_headers(user))
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == plan.name
        assert len(data["days"]) == 3
        assert len(data["days"][0]["exercises"]) == 1
        ex = data["days"][0]["exercises"][0]
        assert "sets" in ex and "rep_low" in ex and "primary_purpose" in ex

    def test_returns_404_for_missing(self, client, db):
        user = make_user(db)
        resp = client.get("/workouts/9999", headers=auth_headers(user))
        assert resp.status_code == 404


class TestRecordViewAPI:
    def test_increments_views_once_per_user(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db, views=0)
        resp = client.post(f"/workouts/{plan.id}/view", headers=auth_headers(user))
        assert resp.status_code == 200
        assert resp.json()["views"] == 1
        resp = client.post(f"/workouts/{plan.id}/view", headers=auth_headers(user))
        assert resp.json()["views"] == 1  # no double-count!

    def test_different_users_increment_separately(self, client, db):
        user1 = make_user(db, username="u1", email="u1@test.com")
        user2 = make_user(db, username="u2", email="u2@test.com")
        plan = _seed_plan(db, views=0)
        client.post(f"/workouts/{plan.id}/view", headers=auth_headers(user1))
        resp = client.post(f"/workouts/{plan.id}/view", headers=auth_headers(user2))
        assert resp.json()["views"] == 2

    def test_returns_404_for_missing(self, client, db):
        user = make_user(db)
        resp = client.post("/workouts/9999/view", headers=auth_headers(user))
        assert resp.status_code == 404


class TestRatePlanAPI:
    def test_rate_plan_first_time(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        resp = client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 4.5},
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rating"] == 4.5
        assert data["rating_count"] == 1
        assert data["my_rating"] == 4.5

    def test_update_existing_rating(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 3.0},
            headers=auth_headers(user),
        )
        resp = client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 5.0},
            headers=auth_headers(user),
        )
        data = resp.json()
        assert data["rating"] == 5.0
        assert data["rating_count"] == 1
        assert data["my_rating"] == 5.0

    def test_multiple_users_average(self, client, db):
        user1 = make_user(db, username="r1", email="r1@test.com")
        user2 = make_user(db, username="r2", email="r2@test.com")
        plan = _seed_plan(db)
        client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 4.0},
            headers=auth_headers(user1),
        )
        resp = client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 5.0},
            headers=auth_headers(user2),
        )
        data = resp.json()
        assert data["rating"] == 4.5
        assert data["rating_count"] == 2

    def test_invalid_score_rejected(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        resp = client.post(
            f"/workouts/{plan.id}/rate",
            json={"score": 6.0},
            headers=auth_headers(user),
        )
        assert resp.status_code == 422

    def test_returns_404_for_missing(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/workouts/9999/rate",
            json={"score": 3.0},
            headers=auth_headers(user),
        )
        assert resp.status_code == 404
