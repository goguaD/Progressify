"""Unit tests for app.services.strength_standards."""
import pytest

from app.services.strength_standards import (
    EXERCISE_MUSCLES,
    LEVELS,
    STRENGTH_STANDARDS,
    classify_lift,
    compute_muscle_levels,
)


class TestClassifyLift:
    def test_returns_none_for_unknown_exercise(self):
        assert classify_lift("Unknown Move", 100, 80, "male") is None

    def test_returns_none_for_zero_weight(self):
        assert classify_lift("Barbell Bench Press", 0, 80, "male") is None

    def test_returns_none_for_zero_bodyweight(self):
        assert classify_lift("Barbell Bench Press", 100, 0, "male") is None

    def test_male_bench_tiers(self):
        # Thresholds: novice 0.75, intermediate 1.25, advanced 1.75, elite 2.25
        bw = 80.0
        assert classify_lift("Barbell Bench Press", 30, bw, "male") == "beginner"
        assert classify_lift("Barbell Bench Press", 60, bw, "male") == "beginner"  # at novice
        assert classify_lift("Barbell Bench Press", 100, bw, "male") == "intermediate"
        assert classify_lift("Barbell Bench Press", 140, bw, "male") == "advanced"
        assert classify_lift("Barbell Bench Press", 180, bw, "male") == "elite"

    def test_female_uses_different_thresholds(self):
        # Female bench: novice 0.5, intermediate 0.75, advanced 1.0, elite 1.4
        bw = 60.0
        assert classify_lift("Barbell Bench Press", 30, bw, "female") == "beginner"
        assert classify_lift("Barbell Bench Press", 60, bw, "female") == "advanced"
        assert classify_lift("Barbell Bench Press", 90, bw, "female") == "elite"

    def test_unknown_gender_falls_back_to_male(self):
        assert classify_lift("Barbell Bench Press", 180, 80, "x") == "elite"

    def test_returns_one_of_four_levels(self):
        for ex in STRENGTH_STANDARDS:
            result = classify_lift(ex, 50, 75, "male")
            assert result is None or result in LEVELS


class TestComputeMuscleLevels:
    def test_empty_lifts(self):
        assert compute_muscle_levels([], 80, "male") == {}

    def test_no_bodyweight(self):
        lifts = [{"exercise_name": "Barbell Bench Press", "weight_kg": 100}]
        assert compute_muscle_levels(lifts, None, "male") == {}
        assert compute_muscle_levels(lifts, 0, "male") == {}

    def test_primary_muscle_gets_full_level(self):
        # Elite bench → chest=elite
        lifts = [{"exercise_name": "Barbell Bench Press", "weight_kg": 200}]
        result = compute_muscle_levels(lifts, 80, "male")
        assert result["chest"] == "elite"

    def test_secondary_muscles_step_down(self):
        # Elite bench → triceps, deltoids should be advanced (one tier below)
        lifts = [{"exercise_name": "Barbell Bench Press", "weight_kg": 200}]
        result = compute_muscle_levels(lifts, 80, "male")
        assert result["triceps"] == "advanced"
        assert result["deltoids"] == "advanced"

    def test_takes_max_across_lifts(self):
        # Intermediate bench + Elite squat → chest=intermediate, quads=elite
        lifts = [
            {"exercise_name": "Barbell Bench Press", "weight_kg": 100},  # intermediate
            {"exercise_name": "Barbell Back Squat", "weight_kg": 250},   # elite
        ]
        result = compute_muscle_levels(lifts, 80, "male")
        assert result["chest"] == "intermediate"
        assert result["quadriceps"] == "elite"

    def test_ignores_missing_weight(self):
        lifts = [
            {"exercise_name": "Barbell Bench Press", "weight_kg": 0},
            {"exercise_name": "Barbell Bench Press"},
            {},
        ]
        assert compute_muscle_levels(lifts, 80, "male") == {}

    def test_ignores_unknown_exercises(self):
        lifts = [{"exercise_name": "Made Up Lift", "weight_kg": 100}]
        assert compute_muscle_levels(lifts, 80, "male") == {}

    def test_beginner_secondary_stays_beginner(self):
        # Beginner level can't step down further than beginner
        lifts = [{"exercise_name": "Barbell Bench Press", "weight_kg": 30}]
        result = compute_muscle_levels(lifts, 80, "male")
        assert result["chest"] == "beginner"
        assert result.get("triceps") == "beginner"


@pytest.mark.parametrize("ex_name", list(EXERCISE_MUSCLES))
def test_exercise_muscle_map_has_primary(ex_name):
    """Every exercise in the muscle map must have at least one primary muscle."""
    assert EXERCISE_MUSCLES[ex_name]["primary"], f"{ex_name} lacks primary muscle"


def test_all_standards_have_both_genders():
    """Each exercise in STRENGTH_STANDARDS must include male + female thresholds."""
    for ex, std in STRENGTH_STANDARDS.items():
        assert "male" in std, f"{ex} missing male thresholds"
        assert "female" in std, f"{ex} missing female thresholds"
        assert len(std["male"]) == 4
        assert len(std["female"]) == 4
        # Thresholds must be strictly increasing.
        for gender_key in ("male", "female"):
            ascending = std[gender_key]
            assert ascending == sorted(ascending), \
                f"{ex} {gender_key} thresholds not ascending"
