from tests.conftest import auth_headers, make_user


def test_send_friend_request(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    make_user(db, username="bob", email="b@example.com")
    headers = auth_headers(u1)

    resp = client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["ok"] is True


def test_send_request_to_self(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    headers = auth_headers(u1)

    resp = client.post(
        "/friends/request",
        json={"username": "alice"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"].lower()


def test_send_request_nonexistent_user(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    headers = auth_headers(u1)

    resp = client.post(
        "/friends/request",
        json={"username": "nobody"},
        headers=headers,
    )
    assert resp.status_code == 404


def test_send_duplicate_request(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    make_user(db, username="bob", email="b@example.com")
    headers = auth_headers(u1)

    client.post("/friends/request", json={"username": "bob"}, headers=headers)
    resp = client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "already sent" in resp.json()["detail"].lower()


def test_accept_request(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )

    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    assert reqs.status_code == 200
    req_id = reqs.json()[0]["id"]

    resp = client.post(f"/friends/accept/{req_id}", headers=auth_headers(u2))
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_decline_request(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )

    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    req_id = reqs.json()[0]["id"]

    resp = client.post(f"/friends/decline/{req_id}", headers=auth_headers(u2))
    assert resp.status_code == 200


def test_list_friends(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    req_id = reqs.json()[0]["id"]
    client.post(f"/friends/accept/{req_id}", headers=auth_headers(u2))

    resp = client.get("/friends", headers=auth_headers(u1))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == "bob"


def test_list_friends_empty(client, db):
    u1 = make_user(db, username="loner", email="l@example.com")
    resp = client.get("/friends", headers=auth_headers(u1))
    assert resp.status_code == 200
    assert resp.json() == []


def test_remove_friend(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    req_id = reqs.json()[0]["id"]
    client.post(f"/friends/accept/{req_id}", headers=auth_headers(u2))

    resp = client.delete(f"/friends/{u2.id}", headers=auth_headers(u1))
    assert resp.status_code == 200

    friends = client.get("/friends", headers=auth_headers(u1))
    assert len(friends.json()) == 0


def test_remove_nonexistent_friend(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    resp = client.delete("/friends/999", headers=auth_headers(u1))
    assert resp.status_code == 404


def test_auto_accept_reverse_request(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    resp = client.post(
        "/friends/request",
        json={"username": "alice"},
        headers=auth_headers(u2),
    )
    assert resp.status_code == 201
    assert resp.json().get("auto_accepted") is True


def test_already_friends(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    req_id = reqs.json()[0]["id"]
    client.post(f"/friends/accept/{req_id}", headers=auth_headers(u2))

    resp = client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    assert resp.status_code == 400
    assert "already friends" in resp.json()["detail"].lower()


def test_pending_requests_list(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )

    resp = client.get("/friends/requests", headers=auth_headers(u2))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["requester"]["username"] == "alice"


def test_accept_wrong_user(client, db):
    u1 = make_user(db, username="alice", email="a@example.com")
    u2 = make_user(db, username="bob", email="b@example.com")
    u3 = make_user(db, username="charlie", email="c@example.com")

    client.post(
        "/friends/request",
        json={"username": "bob"},
        headers=auth_headers(u1),
    )
    reqs = client.get("/friends/requests", headers=auth_headers(u2))
    req_id = reqs.json()[0]["id"]

    resp = client.post(f"/friends/accept/{req_id}", headers=auth_headers(u3))
    assert resp.status_code == 404
