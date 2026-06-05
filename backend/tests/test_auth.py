from tests.conftest import auth_headers, make_user


def test_register_success(client, db):
    resp = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "firstname": "New",
            "lastname": "User",
            "email": "new@example.com",
            "password": "secret123",
            "gender": "male",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"


def test_register_duplicate_email(client, db):
    make_user(db, username="existing", email="dup@example.com")
    resp = client.post(
        "/auth/register",
        json={
            "username": "other",
            "firstname": "O",
            "lastname": "U",
            "email": "dup@example.com",
            "password": "pass",
            "gender": "female",
        },
    )
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_register_duplicate_username(client, db):
    make_user(db, username="taken", email="a@example.com")
    resp = client.post(
        "/auth/register",
        json={
            "username": "taken",
            "firstname": "T",
            "lastname": "U",
            "email": "b@example.com",
            "password": "pass",
            "gender": "male",
        },
    )
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


def test_register_invalid_username(client, db):
    resp = client.post(
        "/auth/register",
        json={
            "username": "AB",
            "firstname": "A",
            "lastname": "B",
            "email": "c@example.com",
            "password": "pass",
            "gender": "male",
        },
    )
    assert resp.status_code == 422


def test_register_invalid_gender(client, db):
    resp = client.post(
        "/auth/register",
        json={
            "username": "validuser",
            "firstname": "A",
            "lastname": "B",
            "email": "d@example.com",
            "password": "pass",
            "gender": "other",
        },
    )
    assert resp.status_code == 422


def test_login_success(client, db):
    make_user(db, username="loginuser", email="login@example.com", password="mypass")
    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "mypass"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"


def test_login_wrong_password(client, db):
    make_user(db, username="user1", email="u1@example.com", password="right")
    resp = client.post(
        "/auth/login",
        json={"email": "u1@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_nonexistent_email(client, db):
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "x"},
    )
    assert resp.status_code == 401


def test_logout(client, db):
    user = make_user(db, username="logoutuser", email="lo@example.com")
    headers = auth_headers(user)
    resp = client.post("/auth/logout", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_me_unauthenticated(client, db):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_authenticated(client, db):
    user = make_user(db, username="meuser", email="me@example.com")
    headers = auth_headers(user)
    resp = client.get("/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "meuser"


def test_me_invalid_token(client, db):
    resp = client.get("/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
