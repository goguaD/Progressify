from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.services.user_service import is_online, placeholder_activity, public_user_dict


def _make_user(**kwargs):
    defaults = {
        "id": 1,
        "username": "testuser",
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "goal": None,
        "weight": None,
        "height": None,
        "gender": "male",
        "avatar_url": None,
        "role": "user",
        "last_seen": datetime.now(UTC),
        "is_online": True,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestIsOnline:
    def test_online_recent(self):
        u = _make_user(is_online=True, last_seen=datetime.now(UTC))
        assert is_online(u) is True

    def test_offline_flag(self):
        u = _make_user(is_online=False, last_seen=datetime.now(UTC))
        assert is_online(u) is False

    def test_no_last_seen(self):
        u = _make_user(is_online=True, last_seen=None)
        assert is_online(u) is False

    def test_stale_last_seen(self):
        stale = datetime.now(UTC) - timedelta(minutes=5)
        u = _make_user(is_online=True, last_seen=stale)
        assert is_online(u) is False

    def test_naive_last_seen(self):
        u = _make_user(
            is_online=True,
            last_seen=datetime.now().replace(tzinfo=None),
        )
        result = is_online(u)
        assert isinstance(result, bool)


class TestPublicUserDict:
    def test_returns_expected_keys(self):
        u = _make_user()
        d = public_user_dict(u)
        assert d["id"] == 1
        assert d["username"] == "testuser"
        assert "is_online" in d
        assert "password_hash" not in d

    def test_is_online_derived(self):
        u = _make_user(is_online=False)
        d = public_user_dict(u)
        assert d["is_online"] is False


class TestPlaceholderActivity:
    def test_muscle_gain(self):
        u = _make_user(goal="muscle_gain")
        act = placeholder_activity(u)
        assert "Chest" in act["current_workout"]
        assert "Protein" in act["current_meal_plan"]

    def test_no_goal(self):
        u = _make_user(goal=None)
        act = placeholder_activity(u)
        assert act["current_workout"] == "No workout yet"

    def test_active_right_now(self):
        u = _make_user(
            is_online=True,
            last_seen=datetime.now(UTC),
        )
        act = placeholder_activity(u)
        assert act["last_activity"] == "Active right now"

    def test_last_seen_minutes(self):
        u = _make_user(
            is_online=False,
            last_seen=datetime.now(UTC) - timedelta(minutes=15),
        )
        act = placeholder_activity(u)
        assert "min ago" in act["last_activity"]

    def test_last_seen_hours(self):
        u = _make_user(
            is_online=False,
            last_seen=datetime.now(UTC) - timedelta(hours=5),
        )
        act = placeholder_activity(u)
        assert "h ago" in act["last_activity"]

    def test_last_seen_days(self):
        u = _make_user(
            is_online=False,
            last_seen=datetime.now(UTC) - timedelta(days=3),
        )
        act = placeholder_activity(u)
        assert "d ago" in act["last_activity"]

    def test_never_logged_in(self):
        u = _make_user(last_seen=None)
        act = placeholder_activity(u)
        assert "Hasn't logged in" in act["last_activity"]
