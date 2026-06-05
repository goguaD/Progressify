from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.friend_service import friendship_state


def _make_friendship(**kwargs):
    return SimpleNamespace(**kwargs)


class TestFriendshipState:
    def test_self(self):
        repo = MagicMock()
        state, req_id = friendship_state(repo, 1, 1)
        assert state == "self"
        assert req_id is None

    def test_none_no_row(self):
        repo = MagicMock()
        repo.find_between.return_value = None
        state, req_id = friendship_state(repo, 1, 2)
        assert state == "none"
        assert req_id is None

    def test_accepted(self):
        repo = MagicMock()
        repo.find_between.return_value = _make_friendship(
            id=10, requester_id=1, addressee_id=2, status="accepted"
        )
        state, req_id = friendship_state(repo, 1, 2)
        assert state == "friends"
        assert req_id == 10

    def test_pending_outgoing(self):
        repo = MagicMock()
        repo.find_between.return_value = _make_friendship(
            id=11, requester_id=1, addressee_id=2, status="pending"
        )
        state, req_id = friendship_state(repo, 1, 2)
        assert state == "pending_outgoing"
        assert req_id == 11

    def test_pending_incoming(self):
        repo = MagicMock()
        repo.find_between.return_value = _make_friendship(
            id=12, requester_id=2, addressee_id=1, status="pending"
        )
        state, req_id = friendship_state(repo, 1, 2)
        assert state == "pending_incoming"
        assert req_id == 12

    def test_unknown_status_returns_none(self):
        repo = MagicMock()
        repo.find_between.return_value = _make_friendship(
            id=13, requester_id=1, addressee_id=2, status="deleted"
        )
        state, req_id = friendship_state(repo, 1, 2)
        assert state == "none"
        assert req_id is None
