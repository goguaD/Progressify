from unittest.mock import MagicMock

from app.services.meal_service import DEFAULT_MEALS, GEORGIAN_TRANSLATIONS, meal_out_dict


def _make_meal(**overrides):
    defaults = dict(
        id=1,
        name="Test Meal",
        name_ka="ტესტ კერძი",
        description="desc",
        description_ka="აღწერა",
        image_url="https://img.jpg",
        goal="cut",
        calories=300,
        protein=30.0,
        carbs=20.0,
        fat=10.0,
        fiber=3.0,
        sugar=2.0,
        views=10,
        rating_sum=8.0,
        rating_count=2,
        is_default=True,
        created_at=None,
        author=None,
    )
    defaults.update(overrides)
    meal = MagicMock()
    for k, v in defaults.items():
        setattr(meal, k, v)
    return meal


class TestMealOutDict:
    def test_basic_fields(self):
        meal = _make_meal()
        result = meal_out_dict(meal)

        assert result["id"] == 1
        assert result["name"] == "Test Meal"
        assert result["name_ka"] == "ტესტ კერძი"
        assert result["description"] == "desc"
        assert result["description_ka"] == "აღწერა"
        assert result["goal"] == "cut"
        assert result["calories"] == 300
        assert result["protein"] == 30.0
        assert result["carbs"] == 20.0
        assert result["fat"] == 10.0
        assert result["fiber"] == 3.0
        assert result["sugar"] == 2.0
        assert result["views"] == 10
        assert result["is_default"] is True

    def test_average_rating_calculation(self):
        meal = _make_meal(rating_sum=9.0, rating_count=2)
        result = meal_out_dict(meal)
        assert result["rating"] == 4.5
        assert result["rating_count"] == 2

    def test_average_rating_rounds_to_half(self):
        meal = _make_meal(rating_sum=7.0, rating_count=3)
        result = meal_out_dict(meal)
        assert result["rating"] == 2.5

    def test_zero_ratings(self):
        meal = _make_meal(rating_sum=0, rating_count=0)
        result = meal_out_dict(meal)
        assert result["rating"] == 0.0
        assert result["rating_count"] == 0

    def test_none_rating_count(self):
        meal = _make_meal(rating_sum=0, rating_count=None)
        result = meal_out_dict(meal)
        assert result["rating"] == 0.0
        assert result["rating_count"] == 0

    def test_my_rating_passed(self):
        meal = _make_meal()
        result = meal_out_dict(meal, my_rating=3.5)
        assert result["my_rating"] == 3.5

    def test_my_rating_none(self):
        meal = _make_meal()
        result = meal_out_dict(meal)
        assert result["my_rating"] is None

    def test_added_by_username(self):
        author = MagicMock()
        author.username = "chef"
        meal = _make_meal(author=author)
        result = meal_out_dict(meal)
        assert result["added_by_username"] == "chef"

    def test_no_author(self):
        meal = _make_meal(author=None)
        result = meal_out_dict(meal)
        assert result["added_by_username"] is None


class TestDefaultMeals:
    def test_has_meals(self):
        assert len(DEFAULT_MEALS) > 0

    def test_all_required_fields(self):
        required = {
            "name", "description", "image_url", "goal",
            "calories", "protein", "carbs", "fat",
        }
        for meal in DEFAULT_MEALS:
            assert required.issubset(meal.keys()), f"Missing fields in {meal['name']}"

    def test_valid_goals(self):
        valid = {"cut", "bulk", "maintain", "general", "cheat"}
        for meal in DEFAULT_MEALS:
            assert meal["goal"] in valid, f"Invalid goal '{meal['goal']}' for {meal['name']}"

    def test_has_cheat_meals(self):
        cheat = [m for m in DEFAULT_MEALS if m["goal"] == "cheat"]
        assert len(cheat) >= 3

    def test_goal_distribution(self):
        goals = {m["goal"] for m in DEFAULT_MEALS}
        assert "cut" in goals
        assert "bulk" in goals
        assert "maintain" in goals
        assert "cheat" in goals


class TestGeorgianTranslations:
    def test_translations_exist(self):
        assert len(GEORGIAN_TRANSLATIONS) > 0

    def test_all_default_meals_have_translations(self):
        for meal in DEFAULT_MEALS:
            name = meal["name"]
            assert name in GEORGIAN_TRANSLATIONS, f"Missing Georgian translation for '{name}'"

    def test_translations_have_required_keys(self):
        for name, data in GEORGIAN_TRANSLATIONS.items():
            assert "name_ka" in data, f"Missing name_ka for '{name}'"
            assert "description_ka" in data, f"Missing description_ka for '{name}'"
            assert len(data["name_ka"]) > 0
            assert len(data["description_ka"]) > 0
