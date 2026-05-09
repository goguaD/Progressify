from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.challenge_service import (
    challenge_out,
    compute_h2h,
    parse_result,
    resolve_challenge,
    safe_deadline,
)


def _make_user(uid: int, username: str = "user"):
    return SimpleNamespace(
        id=uid,
        username=username,
        firstname=username.capitalize(),
        lastname="Test",
        avatar_url=None,
        is_online=True,
        last_seen=datetime.now(UTC),
    )


def _make_challenge(**kwargs):
    defaults = {
        "id": 1,
        "challenger_id": 1,
        "opponent_id": 2,
        "challenge_type": "strength",
        "message": None,
        "deadline": datetime.now(UTC) + timedelta(days=7),
        "muscle_group": "chest",
        "endurance_mode": None,
        "endurance_speed": None,
        "endurance_gradient": None,
        "target_weight_kg": None,
        "status": "accepted",
        "challenger_result": None,
        "opponent_result": None,
        "challenger_submitted_at": None,
        "opponent_submitted_at": None,
        "winner_id": None,
        "deadline_notified": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    ch = SimpleNamespace(**defaults)
    ch.challenger = _make_user(ch.challenger_id, "challenger")
    ch.opponent = _make_user(ch.opponent_id, "opponent")
    ch.winner = _make_user(ch.winner_id) if ch.winner_id else None
    return ch


class TestParseResult:
    def test_none(self):
        assert parse_result(None) is None

    def test_valid_float(self):
        assert parse_result("42.5") == 42.5

    def test_invalid_string(self):
        assert parse_result("abc") is None

    def test_zero(self):
        assert parse_result("0") == 0.0


class TestSafeDeadline:
    def test_none_deadline(self):
        ch = _make_challenge(deadline=None)
        assert safe_deadline(ch) is None

    def test_naive_datetime(self):
        naive = datetime(2026, 6, 1, 12, 0, 0)
        ch = _make_challenge(deadline=naive)
        result = safe_deadline(ch)
        assert result is not None
        assert result.tzinfo == UTC

    def test_aware_datetime(self):
        aware = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
        ch = _make_challenge(deadline=aware)
        assert safe_deadline(ch) == aware


class TestResolveChallenge:
    def test_strength_higher_wins(self):
        repo = MagicMock()
        ch = _make_challenge(
            challenger_result="100",
            opponent_result="80",
            challenger_submitted_at=datetime.now(UTC),
            opponent_submitted_at=datetime.now(UTC),
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id == ch.challenger_id
        assert ch.status == "completed"
        repo.save.assert_called()

    def test_strength_lower_loses(self):
        repo = MagicMock()
        ch = _make_challenge(
            challenger_result="50",
            opponent_result="80",
            challenger_submitted_at=datetime.now(UTC),
            opponent_submitted_at=datetime.now(UTC),
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id == ch.opponent_id

    def test_strength_draw(self):
        repo = MagicMock()
        ch = _make_challenge(
            challenger_result="50",
            opponent_result="50",
            challenger_submitted_at=datetime.now(UTC),
            opponent_submitted_at=datetime.now(UTC),
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id is None
        assert ch.status == "completed"

    def test_auto_loss_deadline_passed_one_submitted(self):
        repo = MagicMock()
        past = datetime.now(UTC) - timedelta(hours=1)
        ch = _make_challenge(
            deadline=past,
            challenger_result="100",
            challenger_submitted_at=datetime.now(UTC),
            opponent_result=None,
            opponent_submitted_at=None,
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id == ch.challenger_id
        assert ch.status == "completed"

    def test_target_weight_first_submission_wins(self):
        repo = MagicMock()
        now = datetime.now(UTC)
        ch = _make_challenge(
            challenge_type="target_weight",
            deadline=None,
            target_weight_kg=70.0,
            challenger_result="70",
            challenger_submitted_at=now,
            opponent_result=None,
            opponent_submitted_at=None,
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id == ch.challenger_id
        assert ch.status == "completed"

    def test_target_weight_opponent_first(self):
        repo = MagicMock()
        now = datetime.now(UTC)
        ch = _make_challenge(
            challenge_type="target_weight",
            deadline=None,
            target_weight_kg=70.0,
            challenger_result=None,
            challenger_submitted_at=None,
            opponent_result="70",
            opponent_submitted_at=now,
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id == ch.opponent_id

    def test_no_resolution_without_both_and_no_deadline(self):
        repo = MagicMock()
        ch = _make_challenge(
            challenger_result="100",
            challenger_submitted_at=datetime.now(UTC),
        )
        resolve_challenge(ch, repo)
        assert ch.status == "accepted"
        repo.save.assert_not_called()

    def test_both_none_results_deadline_passed(self):
        repo = MagicMock()
        past = datetime.now(UTC) - timedelta(hours=1)
        ch = _make_challenge(
            deadline=past,
            challenger_result=None,
            challenger_submitted_at=None,
            opponent_result=None,
            opponent_submitted_at=None,
        )
        resolve_challenge(ch, repo)
        assert ch.winner_id is None
        assert ch.status == "completed"


class TestChallengeOut:
    def test_basic_output(self):
        ch = _make_challenge()
        result = challenge_out(ch, ch.challenger_id)
        assert result["id"] == ch.id
        assert result["status"] == "accepted"
        assert result["challenger"]["username"] == "challenger"

    def test_results_hidden_before_both_submit(self):
        ch = _make_challenge(
            challenger_result="100",
            challenger_submitted_at=datetime.now(UTC),
        )
        result = challenge_out(ch, ch.challenger_id)
        assert result["my_result"] is None
        assert result["my_submitted"] is True

    def test_results_visible_when_completed(self):
        ch = _make_challenge(
            status="completed",
            challenger_result="100",
            opponent_result="80",
            challenger_submitted_at=datetime.now(UTC),
            opponent_submitted_at=datetime.now(UTC),
            winner_id=1,
        )
        result = challenge_out(ch, ch.challenger_id)
        assert result["my_result"] == 100.0
        assert result["their_result"] == 80.0


class TestComputeH2H:
    def test_empty(self):
        repo = MagicMock()
        repo.completed_between.return_value = []
        scores = compute_h2h(repo, 1, 2)
        assert scores == {"wins": 0, "losses": 0, "draws": 0}

    def test_with_results(self):
        ch1 = _make_challenge(winner_id=1)
        ch2 = _make_challenge(winner_id=2)
        ch3 = _make_challenge(winner_id=None)
        repo = MagicMock()
        repo.completed_between.return_value = [ch1, ch2, ch3]
        scores = compute_h2h(repo, 1, 2)
        assert scores == {"wins": 1, "losses": 1, "draws": 1}
