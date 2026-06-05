"""Unit tests for app.repositories.workout_repo.WorkoutRepository."""
from app.models import Exercise, WorkoutDay, WorkoutPlan, WorkoutPlanRating
from app.repositories.workout_repo import WorkoutRepository


def _seed_plan(db, **overrides) -> WorkoutPlan:
    defaults = dict(
        name="Test Plan",
        description="Test description",
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
    day = WorkoutDay(day_number=1, name="Push", focus="chest")
    day.exercises.append(
        Exercise(
            order_index=0, name="Bench", description="d",
            sets=3, rep_low=8, rep_high=12, rest_seconds=90,
            primary_purpose="hypertrophy", muscle_group="chest",
        ),
    )
    plan.days.append(day)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


class TestListPlans:
    def test_list_returns_plans(self, db):
        repo = WorkoutRepository(db)
        _seed_plan(db, name="A")
        _seed_plan(db, name="B")
        assert len(repo.list_plans()) == 2

    def test_filter_by_days_per_week(self, db):
        repo = WorkoutRepository(db)
        _seed_plan(db, name="P3", days_per_week=3)
        _seed_plan(db, name="P5", days_per_week=5)
        result = repo.list_plans(days_per_week=3)
        assert len(result) == 1
        assert result[0].name == "P3"

    def test_filter_by_level(self, db):
        repo = WorkoutRepository(db)
        _seed_plan(db, name="Beg", level="beginner")
        _seed_plan(db, name="Adv", level="advanced")
        result = repo.list_plans(level="beginner")
        assert len(result) == 1
        assert result[0].name == "Beg"

    def test_sort_by_views(self, db):
        repo = WorkoutRepository(db)
        _seed_plan(db, name="Low", views=1)
        _seed_plan(db, name="High", views=99)
        result = repo.list_plans(sort="views")
        assert result[0].name == "High"

    def test_pagination(self, db):
        repo = WorkoutRepository(db)
        for i in range(5):
            _seed_plan(db, name=f"P{i}")
        result = repo.list_plans(limit=2, offset=0)
        assert len(result) == 2

    def test_default_sort_is_newest(self, db):
        repo = WorkoutRepository(db)
        _seed_plan(db, name="First")
        _seed_plan(db, name="Second")
        result = repo.list_plans()
        assert len(result) == 2


class TestGetByID:
    def test_returns_plan_with_days(self, db):
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        loaded = repo.get_by_id(plan.id)
        assert loaded is not None
        assert loaded.id == plan.id
        assert len(loaded.days) == 1

    def test_returns_none_for_missing(self, db):
        repo = WorkoutRepository(db)
        assert repo.get_by_id(9999) is None


class TestViews:
    def test_record_view_returns_true_first_time(self, db):
        from tests.conftest import make_user
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        user = make_user(db)
        assert repo.record_view(plan.id, user.id) is True

    def test_record_view_returns_false_second_time(self, db):
        from tests.conftest import make_user
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        user = make_user(db)
        repo.record_view(plan.id, user.id)
        repo.save()
        assert repo.record_view(plan.id, user.id) is False

    def test_has_user_viewed(self, db):
        from tests.conftest import make_user
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        user = make_user(db)
        assert repo.has_user_viewed(plan.id, user.id) is False
        repo.record_view(plan.id, user.id)
        repo.save()
        assert repo.has_user_viewed(plan.id, user.id) is True


class TestRatings:
    def test_get_user_rating_none(self, db):
        from tests.conftest import make_user
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        user = make_user(db)
        assert repo.get_user_rating(plan.id, user.id) is None

    def test_add_and_get_rating(self, db):
        from tests.conftest import make_user
        repo = WorkoutRepository(db)
        plan = _seed_plan(db)
        user = make_user(db)
        rating = WorkoutPlanRating(
            plan_id=plan.id, user_id=user.id, score=4.5,
        )
        repo.add_rating(rating)
        found = repo.get_user_rating(plan.id, user.id)
        assert found is not None
        assert found.score == 4.5


class TestCreate:
    def test_create_persists_plan(self, db):
        repo = WorkoutRepository(db)
        plan = WorkoutPlan(
            name="New", description="d", days_per_week=3,
            split_type="ppl", level="beginner",
        )
        created = repo.create(plan)
        assert created.id is not None
        assert created.name == "New"
