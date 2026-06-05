"""Unit tests for app.services.workout_service."""
from app.models import Exercise, WorkoutDay, WorkoutPlan
from app.services.workout_service import (
    DEFAULT_PLANS,
    E,
    _parse_reps,
    build_plan_models,
    day_dict,
    exercise_dict,
    plan_detail_dict,
    plan_summary_dict,
    purpose_from_reps,
)


class TestPurposeFromReps:
    def test_low_reps_is_strength(self):
        assert purpose_from_reps(1, 5) == "strength"
        assert purpose_from_reps(3, 5) == "strength"
        assert purpose_from_reps(4, 6) == "strength"  # mid 5

    def test_mid_reps_is_hypertrophy(self):
        assert purpose_from_reps(6, 10) == "hypertrophy"
        assert purpose_from_reps(8, 12) == "hypertrophy"
        assert purpose_from_reps(10, 12) == "hypertrophy"

    def test_high_reps_is_endurance(self):
        assert purpose_from_reps(12, 15) == "endurance"
        assert purpose_from_reps(15, 20) == "endurance"
        assert purpose_from_reps(20, 25) == "endurance"

    def test_boundary_at_5(self):
        assert purpose_from_reps(5, 5) == "strength"

    def test_boundary_at_12(self):
        assert purpose_from_reps(10, 14) == "hypertrophy"  # mid 12


class TestParseReps:
    def test_range(self):
        assert _parse_reps("8-12") == (8, 12)

    def test_range_with_spaces(self):
        assert _parse_reps("8 - 12") == (8, 12)

    def test_single_string(self):
        assert _parse_reps("10") == (10, 10)

    def test_single_int(self):
        assert _parse_reps(10) == (10, 10)


class TestBuildPlanModels:
    def test_builds_plan_with_days_and_exercises(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        assert isinstance(plan, WorkoutPlan)
        assert plan.name == DEFAULT_PLANS[0]["name"]
        assert plan.is_default is True
        assert len(plan.days) == 3
        for d in plan.days:
            assert isinstance(d, WorkoutDay)
            assert len(d.exercises) > 0

    def test_exercise_has_purpose_derived_from_reps(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        for d in plan.days:
            for ex in d.exercises:
                assert ex.primary_purpose in {"strength", "hypertrophy", "endurance"}
                expected = purpose_from_reps(ex.rep_low, ex.rep_high)
                assert ex.primary_purpose == expected

    def test_exercise_carries_image_and_muscle(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        first_ex = plan.days[0].exercises[0]
        assert first_ex.muscle_group
        assert first_ex.image_url

    def test_day_numbers_are_sequential(self):
        for spec in DEFAULT_PLANS:
            plan = build_plan_models(spec)
            assert [d.day_number for d in plan.days] == list(range(1, len(plan.days) + 1))


class TestDefaultPlans:
    def test_has_plans_for_3_4_5_days(self):
        days = {p["days_per_week"] for p in DEFAULT_PLANS}
        assert days == {3, 4, 5}

    def test_each_plan_has_required_fields(self):
        for spec in DEFAULT_PLANS:
            assert "name" in spec
            assert "description" in spec
            assert "days_per_week" in spec
            assert "split_type" in spec
            assert "days" in spec
            assert len(spec["days"]) > 0

    def test_each_day_matches_days_per_week(self):
        for spec in DEFAULT_PLANS:
            assert len(spec["days"]) == spec["days_per_week"]

    def test_all_referenced_exercise_keys_exist(self):
        for spec in DEFAULT_PLANS:
            for day in spec["days"]:
                for entry in day["exercises"]:
                    key = entry[0]
                    assert key in E, f"Missing exercise template: {key}"


class TestSerializers:
    def test_plan_summary_dict(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        plan.id = 1
        plan.views = 5
        plan.rating_sum = 8.5
        plan.rating_count = 2
        d = plan_summary_dict(plan, my_rating=4.0)
        assert d["name"] == plan.name
        assert d["days_per_week"] == 3
        assert d["views"] == 5
        assert d["rating"] == 4.25
        assert d["rating_count"] == 2
        assert d["my_rating"] == 4.0
        assert "days" not in d

    def test_plan_summary_dict_no_ratings(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        plan.id = 1
        plan.rating_sum = 0.0
        plan.rating_count = 0
        d = plan_summary_dict(plan)
        assert d["rating"] == 0.0
        assert d["my_rating"] is None

    def test_plan_detail_dict_includes_days(self):
        plan = build_plan_models(DEFAULT_PLANS[0])
        plan.id = 1
        plan.rating_sum = 0.0
        plan.rating_count = 0
        for i, d in enumerate(plan.days, start=1):
            d.id = i
            for j, ex in enumerate(d.exercises, start=1):
                ex.id = j
        d = plan_detail_dict(plan)
        assert "days" in d
        assert len(d["days"]) == 3
        assert "exercises" in d["days"][0]

    def test_exercise_dict_has_all_fields(self):
        ex = Exercise(
            id=1,
            order_index=0,
            name="Test",
            description="Desc",
            sets=3,
            rep_low=8,
            rep_high=12,
            rest_seconds=90,
            primary_purpose="hypertrophy",
            muscle_group="chest",
        )
        d = exercise_dict(ex)
        assert d["sets"] == 3
        assert d["rep_low"] == 8
        assert d["rep_high"] == 12
        assert d["primary_purpose"] == "hypertrophy"

    def test_day_dict_serializes_exercises(self):
        day = WorkoutDay(id=1, day_number=1, name="Push", focus="chest")
        day.exercises = [
            Exercise(
                id=1, order_index=0, name="Bench", description="d",
                sets=4, rep_low=6, rep_high=8, rest_seconds=120,
                primary_purpose="strength", muscle_group="chest",
            ),
        ]
        d = day_dict(day)
        assert d["name"] == "Push"
        assert len(d["exercises"]) == 1
        assert d["exercises"][0]["name"] == "Bench"
