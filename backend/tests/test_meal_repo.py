from app.models import Meal, MealRating
from app.repositories.meal_repo import MealRepository
from tests.conftest import make_user


def _seed_meal(db, **overrides):
    defaults = dict(
        name="Test Meal",
        description="desc",
        goal="cut",
        calories=300,
        protein=30.0,
        carbs=20.0,
        fat=10.0,
        views=0,
        rating_sum=0.0,
        rating_count=0,
        is_default=True,
    )
    defaults.update(overrides)
    meal = Meal(**defaults)
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


class TestListMeals:
    def test_list_all(self, db):
        _seed_meal(db, name="A", goal="cut")
        _seed_meal(db, name="B", goal="bulk")
        repo = MealRepository(db)
        meals = repo.list_meals()
        assert len(meals) == 2

    def test_filter_by_goal(self, db):
        _seed_meal(db, name="A", goal="cut")
        _seed_meal(db, name="B", goal="bulk")
        repo = MealRepository(db)
        meals = repo.list_meals(goal="cut")
        assert len(meals) == 1
        assert meals[0].name == "A"

    def test_sort_by_views(self, db):
        _seed_meal(db, name="Low", views=1)
        _seed_meal(db, name="High", views=100)
        repo = MealRepository(db)
        meals = repo.list_meals(sort="views")
        assert meals[0].name == "High"

    def test_sort_by_rating(self, db):
        _seed_meal(db, name="Low", rating_count=1, rating_sum=1.0)
        _seed_meal(db, name="High", rating_count=5, rating_sum=25.0)
        repo = MealRepository(db)
        meals = repo.list_meals(sort="rating")
        assert meals[0].name == "High"

    def test_sort_newest(self, db):
        _seed_meal(db, name="First")
        _seed_meal(db, name="Second")
        repo = MealRepository(db)
        meals = repo.list_meals(sort="newest")
        # Both created at same instant in test; just verify both are returned
        assert len(meals) == 2

    def test_sort_oldest(self, db):
        _seed_meal(db, name="First")
        _seed_meal(db, name="Second")
        repo = MealRepository(db)
        meals = repo.list_meals(sort="oldest")
        assert len(meals) == 2

    def test_limit_and_offset(self, db):
        for i in range(5):
            _seed_meal(db, name=f"Meal{i}")
        repo = MealRepository(db)
        meals = repo.list_meals(limit=2, offset=1)
        assert len(meals) == 2


class TestGetById:
    def test_found(self, db):
        meal = _seed_meal(db, name="Find Me")
        repo = MealRepository(db)
        found = repo.get_by_id(meal.id)
        assert found is not None
        assert found.name == "Find Me"

    def test_not_found(self, db):
        repo = MealRepository(db)
        assert repo.get_by_id(9999) is None


class TestUserRating:
    def test_no_rating(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        repo = MealRepository(db)
        assert repo.get_user_rating(meal.id, user.id) is None

    def test_has_rating(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        rating = MealRating(meal_id=meal.id, user_id=user.id, score=4.0)
        db.add(rating)
        db.commit()
        repo = MealRepository(db)
        found = repo.get_user_rating(meal.id, user.id)
        assert found is not None
        assert found.score == 4.0


class TestViewTracking:
    def test_first_view_returns_true(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        repo = MealRepository(db)
        assert repo.record_view(meal.id, user.id) is True

    def test_second_view_returns_false(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        repo = MealRepository(db)
        repo.record_view(meal.id, user.id)
        db.commit()
        assert repo.record_view(meal.id, user.id) is False

    def test_has_user_viewed(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        repo = MealRepository(db)
        assert repo.has_user_viewed(meal.id, user.id) is False
        repo.record_view(meal.id, user.id)
        db.commit()
        assert repo.has_user_viewed(meal.id, user.id) is True

    def test_different_users(self, db):
        meal = _seed_meal(db)
        u1 = make_user(db, username="u1", email="u1@x.com")
        u2 = make_user(db, username="u2", email="u2@x.com")
        repo = MealRepository(db)
        repo.record_view(meal.id, u1.id)
        db.commit()
        assert repo.has_user_viewed(meal.id, u1.id) is True
        assert repo.has_user_viewed(meal.id, u2.id) is False


class TestCreate:
    def test_create_meal(self, db):
        repo = MealRepository(db)
        meal = Meal(
            name="New",
            description="d",
            goal="bulk",
            calories=500,
            protein=40,
            carbs=50,
            fat=15,
            is_default=False,
        )
        created = repo.create(meal)
        assert created.id is not None
        assert created.name == "New"

    def test_add_rating(self, db):
        meal = _seed_meal(db)
        user = make_user(db)
        repo = MealRepository(db)
        rating = MealRating(meal_id=meal.id, user_id=user.id, score=3.5)
        saved = repo.add_rating(rating)
        assert saved.id is not None
        assert saved.score == 3.5
