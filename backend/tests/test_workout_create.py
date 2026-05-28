"""Integration tests for POST /workouts (user-submitted plans)."""
import io
import json

from app.models import Exercise, WorkoutPlan
from app.services.workout_service import _parse_muscle_targets
from tests.conftest import auth_headers, make_user


def _basic_payload(**overrides) -> dict:
    payload = {
        "name": "My Custom Plan",
        "name_ka": "ჩემი პროგრამა",
        "description": "Three full-body sessions per week.",
        "description_ka": "სრული სხეულის ვარჯიში სამჯერ კვირაში.",
        "days_per_week": 2,
        "split_type": "custom",
        "level": "intermediate",
        "days": [
            {
                "day_number": 1,
                "name": "Day A",
                "name_ka": "დღე ა",
                "focus": "Push",
                "exercises": [
                    {
                        "name": "Bench Press",
                        "name_ka": "ბენჩ პრესი",
                        "description": "Press the bar.",
                        "sets": 4, "rep_low": 6, "rep_high": 10, "rest_seconds": 120,
                        "primary_purpose": "hypertrophy",
                        "muscle_group": "chest",
                        "muscle_targets": [
                            {"slug": "chest",    "intensity": "high"},
                            {"slug": "triceps",  "intensity": "medium"},
                            {"slug": "deltoids", "intensity": "low"},
                        ],
                    },
                ],
            },
            {
                "day_number": 2,
                "name": "Day B",
                "name_ka": "დღე ბ",
                "focus": "Pull",
                "exercises": [
                    {
                        "name": "Pull-Up",
                        "name_ka": "Pull-Up",
                        "description": "Hang and pull.",
                        "sets": 3, "rep_low": 5, "rep_high": 8, "rest_seconds": 150,
                        "primary_purpose": "strength",
                        "muscle_group": "back",
                        "muscle_targets": [
                            {"slug": "upper-back", "intensity": "high"},
                            {"slug": "biceps",     "intensity": "medium"},
                        ],
                    },
                ],
            },
        ],
    }
    payload.update(overrides)
    return payload


class TestCreatePlan:
    def test_requires_auth(self, client):
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(_basic_payload())},
        )
        assert r.status_code in {401, 403}

    def test_creates_plan_with_days_and_exercises(self, client, db):
        user = make_user(db)
        payload = _basic_payload()
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            headers=auth_headers(user),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "My Custom Plan"
        assert data["name_ka"] == "ჩემი პროგრამა"
        assert data["added_by_username"] == user.username
        assert data["is_default"] is False
        assert len(data["days"]) == 2

        # Muscle targets propagate through the API.
        bench = data["days"][0]["exercises"][0]
        assert bench["muscle_targets"] == [
            {"slug": "chest", "intensity": "high"},
            {"slug": "triceps", "intensity": "medium"},
            {"slug": "deltoids", "intensity": "low"},
        ]

        # DB persistence.
        plan = db.query(WorkoutPlan).filter_by(name="My Custom Plan").first()
        assert plan is not None
        assert plan.added_by == user.id
        all_ex = db.query(Exercise).filter(Exercise.day_id.in_(
            [d.id for d in plan.days],
        )).all()
        assert len(all_ex) == 2

    def test_persists_muscle_targets_as_json(self, db, client):
        user = make_user(db)
        client.post(
            "/workouts",
            data={"payload": json.dumps(_basic_payload())},
            headers=auth_headers(user),
        )
        plan = db.query(WorkoutPlan).filter_by(name="My Custom Plan").first()
        bench = plan.days[0].exercises[0]
        parsed = _parse_muscle_targets(bench.muscle_targets)
        assert parsed[0]["slug"] == "chest"
        assert parsed[0]["intensity"] == "high"

    def test_rejects_mismatched_day_count(self, client, db):
        user = make_user(db)
        payload = _basic_payload(days_per_week=3)  # but still 2 days
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            headers=auth_headers(user),
        )
        assert r.status_code == 422

    def test_rejects_invalid_rep_range(self, client, db):
        user = make_user(db)
        payload = _basic_payload()
        payload["days"][0]["exercises"][0]["rep_low"] = 12
        payload["days"][0]["exercises"][0]["rep_high"] = 6
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            headers=auth_headers(user),
        )
        assert r.status_code == 422

    def test_rejects_invalid_purpose(self, client, db):
        user = make_user(db)
        payload = _basic_payload()
        payload["days"][0]["exercises"][0]["primary_purpose"] = "wrong"
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            headers=auth_headers(user),
        )
        assert r.status_code == 422

    def test_rejects_malformed_payload(self, client, db):
        user = make_user(db)
        r = client.post(
            "/workouts",
            data={"payload": "not json"},
            headers=auth_headers(user),
        )
        assert r.status_code == 422

    def test_rejects_empty_day(self, client, db):
        user = make_user(db)
        payload = _basic_payload()
        payload["days"][0]["exercises"] = []
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            headers=auth_headers(user),
        )
        assert r.status_code == 422

    def test_accepts_image_upload(self, client, db, tmp_path):
        user = make_user(db)
        payload = _basic_payload()
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
            b"\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        r = client.post(
            "/workouts",
            data={"payload": json.dumps(payload)},
            files={"image": ("plan.png", io.BytesIO(png_bytes), "image/png")},
            headers=auth_headers(user),
        )
        assert r.status_code == 200
        assert r.json()["image_url"] is not None

    def test_listing_includes_user_plan(self, client, db):
        user = make_user(db)
        client.post(
            "/workouts",
            data={"payload": json.dumps(_basic_payload())},
            headers=auth_headers(user),
        )
        r = client.get("/workouts", headers=auth_headers(user))
        names = {p["name"] for p in r.json()}
        assert "My Custom Plan" in names


class TestMuscleTargetParser:
    def test_returns_empty_for_none(self):
        assert _parse_muscle_targets(None) == []

    def test_returns_empty_for_bad_json(self):
        assert _parse_muscle_targets("not json") == []

    def test_filters_invalid_intensity(self):
        raw = json.dumps([
            {"slug": "chest", "intensity": "high"},
            {"slug": "chest", "intensity": "extreme"},
            {"intensity": "low"},
            "not a dict",
        ])
        result = _parse_muscle_targets(raw)
        assert result == [{"slug": "chest", "intensity": "high"}]
