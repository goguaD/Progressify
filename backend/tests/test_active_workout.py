"""Integration tests for the /me/workout-plan endpoints."""
from app.models import Exercise, UserActiveWorkoutPlan, UserOneRepMax, WorkoutDay, WorkoutPlan
from app.repositories.workout_repo import WorkoutRepository
from tests.conftest import auth_headers, make_user


def _seed_plan(db, **overrides) -> WorkoutPlan:
    defaults = dict(
        name="Bench Plan",
        description="Tests",
        days_per_week=3,
        split_type="ppl",
        level="intermediate",
        is_default=True,
        views=0, rating_sum=0.0, rating_count=0,
    )
    defaults.update(overrides)
    plan = WorkoutPlan(**defaults)
    day = WorkoutDay(day_number=1, name="Day 1", focus="chest")
    day.exercises.extend([
        Exercise(
            order_index=0, name="Barbell Bench Press", description="d",
            sets=3, rep_low=5, rep_high=8, rest_seconds=180,
            primary_purpose="strength", muscle_group="chest",
        ),
        Exercise(
            order_index=1, name="Barbell Back Squat", description="d",
            sets=3, rep_low=5, rep_high=8, rest_seconds=180,
            primary_purpose="strength", muscle_group="quadriceps",
        ),
    ])
    plan.days.append(day)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


class TestSetActivePlan:
    def test_requires_auth(self, client):
        resp = client.post("/me/workout-plan", json={"plan_id": 1, "lifts": []})
        assert resp.status_code in {401, 403}

    def test_404_for_unknown_plan(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/me/workout-plan",
            json={"plan_id": 999, "lifts": []},
            headers=auth_headers(user),
        )
        assert resp.status_code == 404

    def test_creates_active_plan_and_lifts(self, client, db):
        user = make_user(db, gender="male")
        user.weight = 80.0
        db.commit()
        plan = _seed_plan(db)

        resp = client.post(
            "/me/workout-plan",
            json={
                "plan_id": plan.id,
                "lifts": [
                    {"exercise_name": "Barbell Bench Press", "weight_kg": 100},
                    {"exercise_name": "Barbell Back Squat", "weight_kg": 200},
                ],
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["plan"]["id"] == plan.id
        assert body["bodyweight_kg"] == 80.0
        # Bench 100/80 = 1.25 → intermediate (>=1.25 & <1.75)
        # Squat 200/80 = 2.5 → advanced (>=2.25 & <3.0)
        lifts_by_name = {lift["exercise_name"]: lift for lift in body["lifts"]}
        assert lifts_by_name["Barbell Bench Press"]["level"] == "intermediate"
        assert lifts_by_name["Barbell Back Squat"]["level"] == "advanced"
        # Computed muscle map should reflect these levels.
        assert body["muscle_levels"]["chest"] == "intermediate"
        assert body["muscle_levels"]["quadriceps"] == "advanced"

    def test_replacing_plan_does_not_duplicate(self, client, db):
        user = make_user(db)
        first = _seed_plan(db, name="First")
        second = _seed_plan(db, name="Second")

        client.post(
            "/me/workout-plan",
            json={"plan_id": first.id, "lifts": []},
            headers=auth_headers(user),
        )
        client.post(
            "/me/workout-plan",
            json={"plan_id": second.id, "lifts": []},
            headers=auth_headers(user),
        )

        rows = db.query(UserActiveWorkoutPlan).filter_by(user_id=user.id).all()
        assert len(rows) == 1
        assert rows[0].plan_id == second.id

    def test_validates_weight_range(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        resp = client.post(
            "/me/workout-plan",
            json={
                "plan_id": plan.id,
                "lifts": [
                    {"exercise_name": "Barbell Bench Press", "weight_kg": 5000},
                ],
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 422


class TestGetActivePlan:
    def test_returns_null_when_no_plan(self, client, db):
        user = make_user(db)
        resp = client.get("/me/workout-plan", headers=auth_headers(user))
        assert resp.status_code == 200
        assert resp.json() is None

    def test_returns_plan_after_setting(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        client.post(
            "/me/workout-plan",
            json={"plan_id": plan.id, "lifts": []},
            headers=auth_headers(user),
        )
        resp = client.get("/me/workout-plan", headers=auth_headers(user))
        assert resp.status_code == 200
        body = resp.json()
        assert body["plan"]["id"] == plan.id
        # All exercises are returned even when no 1RM has been submitted.
        names = {item["exercise_name"] for item in body["lifts"]}
        assert names == {"Barbell Bench Press", "Barbell Back Squat"}
        # has_standard reflects strength_standards table membership.
        for lift in body["lifts"]:
            assert lift["has_standard"] is True


class TestUpdateLifts:
    def test_requires_active_plan(self, client, db):
        user = make_user(db)
        resp = client.patch(
            "/me/workout-plan/lifts",
            json={"lifts": [{"exercise_name": "x", "weight_kg": 1}]},
            headers=auth_headers(user),
        )
        assert resp.status_code == 400

    def test_updates_existing_lift(self, client, db):
        user = make_user(db, gender="male")
        user.weight = 80.0
        db.commit()
        plan = _seed_plan(db)
        client.post(
            "/me/workout-plan",
            json={
                "plan_id": plan.id,
                "lifts": [
                    {"exercise_name": "Barbell Bench Press", "weight_kg": 60},
                ],
            },
            headers=auth_headers(user),
        )
        resp = client.patch(
            "/me/workout-plan/lifts",
            json={
                "lifts": [
                    {"exercise_name": "Barbell Bench Press", "weight_kg": 140},
                ],
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        body = resp.json()
        bench = next(
            lift for lift in body["lifts"]
            if lift["exercise_name"] == "Barbell Bench Press"
        )
        assert bench["weight_kg"] == 140
        assert bench["level"] == "advanced"  # 140/80 = 1.75
        # And only one row exists in the DB.
        rows = db.query(UserOneRepMax).filter_by(user_id=user.id).all()
        assert len(rows) == 1


class TestRemoveActivePlan:
    def test_deletes_active_plan(self, client, db):
        user = make_user(db)
        plan = _seed_plan(db)
        client.post(
            "/me/workout-plan",
            json={"plan_id": plan.id, "lifts": []},
            headers=auth_headers(user),
        )
        resp = client.delete("/me/workout-plan", headers=auth_headers(user))
        assert resp.status_code == 204
        assert db.query(UserActiveWorkoutPlan).filter_by(user_id=user.id).count() == 0


class TestProfileIntegration:
    def test_profile_includes_muscle_levels(self, client, db):
        owner = make_user(db, username="lifter", gender="male")
        owner.weight = 80.0
        db.commit()
        plan = _seed_plan(db)

        client.post(
            "/me/workout-plan",
            json={
                "plan_id": plan.id,
                "lifts": [
                    {"exercise_name": "Barbell Bench Press", "weight_kg": 140},
                ],
            },
            headers=auth_headers(owner),
        )

        viewer = make_user(db, username="viewer", email="viewer@example.com")
        resp = client.get(
            "/users/by-username/lifter", headers=auth_headers(viewer),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["muscle_levels"].get("chest") == "advanced"
        assert body["active_workout"]["plan"]["id"] == plan.id


class TestRepositoryHelpers:
    def test_bulk_upsert_round_trip(self, db):
        user = make_user(db)
        repo = WorkoutRepository(db)
        repo.bulk_upsert_one_rep_max(user.id, [
            ("Barbell Bench Press", 80.0),
            ("Barbell Back Squat", 120.0),
        ])
        # Second call updates one and inserts none.
        repo.bulk_upsert_one_rep_max(user.id, [
            ("Barbell Bench Press", 90.0),
        ])
        rows = {r.exercise_name: r.weight_kg for r in repo.list_one_rep_maxes(user.id)}
        assert rows == {"Barbell Bench Press": 90.0, "Barbell Back Squat": 120.0}

    def test_set_active_plan_idempotent(self, db):
        user = make_user(db)
        plan_a = _seed_plan(db, name="A")
        plan_b = _seed_plan(db, name="B")
        repo = WorkoutRepository(db)
        repo.set_active_plan(user.id, plan_a.id)
        repo.set_active_plan(user.id, plan_b.id)
        active = repo.get_active_plan(user.id)
        assert active and active.plan_id == plan_b.id

    def test_delete_active_plan(self, db):
        user = make_user(db)
        plan = _seed_plan(db)
        repo = WorkoutRepository(db)
        repo.set_active_plan(user.id, plan.id)
        repo.delete_active_plan(user.id)
        assert repo.get_active_plan(user.id) is None
