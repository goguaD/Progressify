from datetime import UTC, datetime, timedelta

from app.models import Friendship
from tests.conftest import auth_headers, make_user


def _befriend(db, u1, u2):
    f = Friendship(requester_id=u1.id, addressee_id=u2.id, status="accepted")
    db.add(f)
    db.commit()


def _future_deadline():
    return (datetime.now(UTC) + timedelta(days=7)).isoformat()


def test_create_strength_challenge(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["challenge_type"] == "strength"
    assert data["muscle_group"] == "chest"
    assert data["status"] == "pending"


def test_create_endurance_treadmill(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "endurance",
            "endurance_mode": "treadmill",
            "endurance_speed": 10.0,
            "endurance_gradient": 5.0,
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["endurance_mode"] == "treadmill"
    assert data["endurance_speed"] == 10.0


def test_create_endurance_stairs(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "endurance",
            "endurance_mode": "stairs",
            "endurance_speed": 8.0,
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 201


def test_create_target_weight(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "target_weight",
            "target_weight_kg": 75.0,
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_weight_kg"] == 75.0
    assert data["deadline"] is None


def test_create_challenge_not_friends(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    make_user(db, username="bob", email="b@example.com")

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "friends" in resp.json()["detail"].lower()


def test_create_challenge_self(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "alice",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400


def test_strength_missing_muscle_group(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "muscle group" in resp.json()["detail"].lower()


def test_strength_missing_deadline(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "deadline" in resp.json()["detail"].lower()


def test_endurance_missing_speed(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "endurance",
            "endurance_mode": "treadmill",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400


def test_target_weight_missing_goal(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "target_weight",
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400


def test_accept_and_submit_strength(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]

    accept_resp = client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))
    assert accept_resp.status_code == 200

    sub1 = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 100.0},
        headers=auth_headers(u1),
    )
    assert sub1.status_code == 200
    assert sub1.json()["my_submitted"] is True

    sub2 = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 80.0},
        headers=auth_headers(u2),
    )
    assert sub2.status_code == 200

    get_resp = client.get(f"/challenges/{ch_id}", headers=auth_headers(u1))
    data = get_resp.json()
    assert data["status"] == "completed"
    assert data["winner"]["username"] == "alice"


def test_strength_draw(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "biceps",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))

    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 50.0},
        headers=auth_headers(u1),
    )
    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 50.0},
        headers=auth_headers(u2),
    )

    data = client.get(f"/challenges/{ch_id}", headers=auth_headers(u1)).json()
    assert data["status"] == "completed"
    assert data["winner"] is None


def test_target_weight_first_wins(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "target_weight",
            "target_weight_kg": 70.0,
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))

    sub = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 70.0},
        headers=auth_headers(u2),
    )
    data = sub.json()
    assert data["status"] == "completed"
    assert data["winner"]["username"] == "bob"


def test_decline_challenge(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]

    resp = client.post(f"/challenges/{ch_id}/decline", headers=auth_headers(u2))
    assert resp.status_code == 200

    data = client.get(f"/challenges/{ch_id}", headers=auth_headers(u1)).json()
    assert data["status"] == "declined"


def test_submit_negative_value(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))

    resp = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": -10.0},
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400


def test_submit_already_submitted(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))

    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 100.0},
        headers=auth_headers(u1),
    )
    resp = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 110.0},
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "already submitted" in resp.json()["detail"].lower()


def test_submit_not_active(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]

    resp = client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 100.0},
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "not active" in resp.json()["detail"].lower()


def test_list_challenges(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )

    resp = client.get("/challenges", headers=auth_headers(u1))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_challenges_filtered(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )

    resp = client.get("/challenges?status=pending", headers=auth_headers(u1))
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp2 = client.get("/challenges?status=accepted", headers=auth_headers(u1))
    assert len(resp2.json()) == 0


def test_get_challenge_not_participant(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    u3 = make_user(db, username="charlie", email="c@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "strength",
            "muscle_group": "chest",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]

    resp = client.get(f"/challenges/{ch_id}", headers=auth_headers(u3))
    assert resp.status_code == 404


def test_head_to_head(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.get(f"/challenges/h2h/{u2.id}", headers=auth_headers(u1))
    assert resp.status_code == 200
    data = resp.json()
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["draws"] == 0


def test_head_to_head_with_completed(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "target_weight",
            "target_weight_kg": 70.0,
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))
    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 70.0},
        headers=auth_headers(u1),
    )

    resp = client.get(f"/challenges/h2h/{u2.id}", headers=auth_headers(u1))
    data = resp.json()
    assert data["wins"] == 1
    assert data["losses"] == 0


def test_endurance_longer_time_wins(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    create_resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "endurance",
            "endurance_mode": "treadmill",
            "endurance_speed": 10.0,
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    ch_id = create_resp.json()["id"]
    client.post(f"/challenges/{ch_id}/accept", headers=auth_headers(u2))

    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 600},
        headers=auth_headers(u1),
    )
    client.post(
        f"/challenges/{ch_id}/submit",
        json={"value": 900},
        headers=auth_headers(u2),
    )

    data = client.get(f"/challenges/{ch_id}", headers=auth_headers(u1)).json()
    assert data["status"] == "completed"
    assert data["winner"]["username"] == "bob"


def test_invalid_challenge_type(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    _befriend(db, u1, u2)

    resp = client.post(
        "/challenges",
        json={
            "opponent_username": "bob",
            "challenge_type": "invalid_type",
            "deadline": _future_deadline(),
        },
        headers=auth_headers(u1),
    )
    assert resp.status_code == 422
