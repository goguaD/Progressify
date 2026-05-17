import io

from app.models import Meal, MealRating
from tests.conftest import auth_headers, make_user


def _seed_meal(db, **overrides):
    defaults = dict(
        name="Test Meal",
        description="A test meal description",
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
    def test_list_meals(self, client, db):
        user = make_user(db)
        _seed_meal(db, name="Cut Meal", goal="cut")
        _seed_meal(db, name="Bulk Meal", goal="bulk")
        resp = client.get("/meals", headers=auth_headers(user))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_filter_by_goal(self, client, db):
        user = make_user(db)
        _seed_meal(db, name="Cut Meal", goal="cut")
        _seed_meal(db, name="Bulk Meal", goal="bulk")
        resp = client.get("/meals?goal=cut", headers=auth_headers(user))
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Cut Meal"

    def test_sort_by_views(self, client, db):
        user = make_user(db)
        _seed_meal(db, name="Low", views=1)
        _seed_meal(db, name="High", views=100)
        resp = client.get("/meals?sort=views", headers=auth_headers(user))
        data = resp.json()
        assert data[0]["name"] == "High"

    def test_sort_by_rating(self, client, db):
        user = make_user(db)
        _seed_meal(db, name="Low", rating_count=1, rating_sum=1.0)
        _seed_meal(db, name="High", rating_count=5, rating_sum=25.0)
        resp = client.get("/meals?sort=rating", headers=auth_headers(user))
        data = resp.json()
        assert data[0]["name"] == "High"

    def test_unauthenticated(self, client, db):
        resp = client.get("/meals")
        assert resp.status_code == 401


class TestGetMeal:
    def test_get_meal(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db, name="Specific")
        resp = client.get(f"/meals/{meal.id}", headers=auth_headers(user))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Specific"

    def test_not_found(self, client, db):
        user = make_user(db)
        resp = client.get("/meals/9999", headers=auth_headers(user))
        assert resp.status_code == 404

    def test_includes_my_rating(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db)
        db.add(MealRating(meal_id=meal.id, user_id=user.id, score=4.0))
        meal.rating_sum = 4.0
        meal.rating_count = 1
        db.commit()
        resp = client.get(f"/meals/{meal.id}", headers=auth_headers(user))
        assert resp.json()["my_rating"] == 4.0

    def test_georgian_fields(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db, name_ka="ტესტი", description_ka="აღწერა")
        resp = client.get(f"/meals/{meal.id}", headers=auth_headers(user))
        data = resp.json()
        assert data["name_ka"] == "ტესტი"
        assert data["description_ka"] == "აღწერა"


class TestRecordView:
    def test_first_view_increments(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db, views=5)
        resp = client.post(f"/meals/{meal.id}/view", headers=auth_headers(user))
        assert resp.status_code == 200
        assert resp.json()["views"] == 6

    def test_second_view_no_increment(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db, views=5)
        headers = auth_headers(user)
        client.post(f"/meals/{meal.id}/view", headers=headers)
        resp = client.post(f"/meals/{meal.id}/view", headers=headers)
        assert resp.json()["views"] == 6

    def test_different_users_both_increment(self, client, db):
        u1 = make_user(db, username="u1", email="u1@x.com")
        u2 = make_user(db, username="u2", email="u2@x.com")
        meal = _seed_meal(db, views=0)
        client.post(f"/meals/{meal.id}/view", headers=auth_headers(u1))
        resp = client.post(f"/meals/{meal.id}/view", headers=auth_headers(u2))
        assert resp.json()["views"] == 2

    def test_not_found(self, client, db):
        user = make_user(db)
        resp = client.post("/meals/9999/view", headers=auth_headers(user))
        assert resp.status_code == 404


class TestRateMeal:
    def test_rate_new(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db)
        resp = client.post(
            f"/meals/{meal.id}/rate",
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
        meal = _seed_meal(db)
        headers = auth_headers(user)
        client.post(f"/meals/{meal.id}/rate", json={"score": 3.0}, headers=headers)
        resp = client.post(f"/meals/{meal.id}/rate", json={"score": 5.0}, headers=headers)
        data = resp.json()
        assert data["rating"] == 5.0
        assert data["rating_count"] == 1
        assert data["my_rating"] == 5.0

    def test_half_star_increment(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db)
        resp = client.post(
            f"/meals/{meal.id}/rate",
            json={"score": 2.5},
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        assert resp.json()["my_rating"] == 2.5

    def test_invalid_score_too_high(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db)
        resp = client.post(
            f"/meals/{meal.id}/rate",
            json={"score": 6.0},
            headers=auth_headers(user),
        )
        assert resp.status_code == 422

    def test_invalid_score_not_half(self, client, db):
        user = make_user(db)
        meal = _seed_meal(db)
        resp = client.post(
            f"/meals/{meal.id}/rate",
            json={"score": 2.3},
            headers=auth_headers(user),
        )
        assert resp.status_code == 422

    def test_not_found(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals/9999/rate",
            json={"score": 3.0},
            headers=auth_headers(user),
        )
        assert resp.status_code == 404

    def test_multiple_users_average(self, client, db):
        u1 = make_user(db, username="u1", email="u1@x.com")
        u2 = make_user(db, username="u2", email="u2@x.com")
        meal = _seed_meal(db)
        client.post(f"/meals/{meal.id}/rate", json={"score": 2.0}, headers=auth_headers(u1))
        resp = client.post(f"/meals/{meal.id}/rate", json={"score": 4.0}, headers=auth_headers(u2))
        data = resp.json()
        assert data["rating"] == 3.0
        assert data["rating_count"] == 2


class TestCreateMeal:
    def test_create_minimal(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals",
            data={
                "name": "My Meal",
                "description": "Tasty meal",
                "goal": "bulk",
                "calories": "500",
                "protein": "40",
                "carbs": "50",
                "fat": "15",
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "My Meal"
        assert data["goal"] == "bulk"
        assert data["calories"] == 500
        assert data["is_default"] is False
        assert data["added_by_username"] == user.username

    def test_create_with_georgian(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals",
            data={
                "name": "My Meal",
                "description": "Tasty meal",
                "name_ka": "ჩემი კერძი",
                "description_ka": "გემრიელი",
                "goal": "cut",
                "calories": "300",
                "protein": "30",
                "carbs": "20",
                "fat": "10",
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name_ka"] == "ჩემი კერძი"
        assert data["description_ka"] == "გემრიელი"

    def test_create_with_image(self, client, db):
        user = make_user(db)
        img = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        resp = client.post(
            "/meals",
            data={
                "name": "Pic Meal",
                "description": "Has a pic",
                "goal": "maintain",
                "calories": "400",
                "protein": "35",
                "carbs": "40",
                "fat": "12",
            },
            files={"image": ("meal.png", img, "image/png")},
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        assert resp.json()["image_url"] is not None
        assert "/static/meals/" in resp.json()["image_url"]

    def test_create_invalid_goal(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals",
            data={
                "name": "Bad Goal",
                "description": "desc",
                "goal": "invalid",
                "calories": "300",
                "protein": "30",
                "carbs": "20",
                "fat": "10",
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 422

    def test_create_cheat_meal(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals",
            data={
                "name": "Healthy Pizza",
                "description": "Cauliflower crust",
                "goal": "cheat",
                "calories": "340",
                "protein": "26",
                "carbs": "18",
                "fat": "16",
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        assert resp.json()["goal"] == "cheat"

    def test_create_with_optional_nutrients(self, client, db):
        user = make_user(db)
        resp = client.post(
            "/meals",
            data={
                "name": "Full Meal",
                "description": "Everything",
                "goal": "general",
                "calories": "400",
                "protein": "35",
                "carbs": "40",
                "fat": "12",
                "fiber": "5",
                "sugar": "8",
            },
            headers=auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["fiber"] == 5.0
        assert data["sugar"] == 8.0

    def test_unauthenticated(self, client, db):
        resp = client.post(
            "/meals",
            data={
                "name": "No Auth",
                "description": "desc",
                "goal": "cut",
                "calories": "300",
                "protein": "30",
                "carbs": "20",
                "fat": "10",
            },
        )
        assert resp.status_code == 401
