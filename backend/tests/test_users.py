import io

from tests.conftest import auth_headers, make_user


def test_search_users(client, db):
    u1 = make_user(db, username="alice", email="alice@example.com")
    make_user(db, username="bob", email="bob@example.com")
    headers = auth_headers(u1)

    resp = client.get("/users/search?q=bob", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == "bob"


def test_search_excludes_self(client, db):
    u1 = make_user(db, username="alice", email="alice@example.com")
    headers = auth_headers(u1)

    resp = client.get("/users/search?q=alice", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_search_hides_admins_for_non_admin(client, db):
    u1 = make_user(db, username="regular", email="reg@example.com")
    make_user(db, username="admin_guy", email="admin@example.com", role="admin")
    headers = auth_headers(u1)

    resp = client.get("/users/search?q=admin", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_get_profile(client, db):
    u1 = make_user(db, username="viewer", email="v@example.com")
    make_user(db, username="target", email="t@example.com")
    headers = auth_headers(u1)

    resp = client.get("/users/by-username/target", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "target"
    assert data["relationship"] == "none"
    assert data["friend_count"] == 0


def test_get_profile_not_found(client, db):
    u1 = make_user(db, username="viewer", email="v@example.com")
    headers = auth_headers(u1)

    resp = client.get("/users/by-username/nonexistent", headers=headers)
    assert resp.status_code == 404


def test_get_own_profile(client, db):
    u1 = make_user(db, username="myself", email="my@example.com")
    headers = auth_headers(u1)

    resp = client.get("/users/by-username/myself", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["relationship"] == "self"


def test_upload_avatar(client, db):
    user = make_user(db, username="avataruser", email="av@example.com")
    headers = auth_headers(user)

    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    resp = client.post(
        "/me/avatar",
        headers=headers,
        files={"file": ("avatar.png", io.BytesIO(fake_png), "image/png")},
    )
    assert resp.status_code == 200
    assert "/static/avatars/" in resp.json()["avatar_url"]


def test_upload_avatar_wrong_type(client, db):
    user = make_user(db, username="badav", email="bad@example.com")
    headers = auth_headers(user)

    resp = client.post(
        "/me/avatar",
        headers=headers,
        files={"file": ("avatar.txt", io.BytesIO(b"text"), "text/plain")},
    )
    assert resp.status_code == 400


def test_delete_avatar(client, db):
    user = make_user(db, username="delavatar", email="del@example.com")
    headers = auth_headers(user)

    resp = client.delete("/me/avatar", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["avatar_url"] is None


def test_admin_list_users(client, db):
    admin = make_user(db, username="adminuser", email="admin@example.com", role="admin")
    make_user(db, username="regular", email="reg@example.com")
    headers = auth_headers(admin)

    resp = client.get("/admin/users", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_admin_list_users_non_admin(client, db):
    user = make_user(db, username="noadmin", email="no@example.com")
    headers = auth_headers(user)

    resp = client.get("/admin/users", headers=headers)
    assert resp.status_code == 403
