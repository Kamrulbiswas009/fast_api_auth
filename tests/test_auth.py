def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docs_url" in data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user_success(client):
    payload = {
        "email": "alice@example.com",
        "username": "alice123",
        "password": "strongPassword123!",
        "full_name": "Alice Wonderland",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice123"
    assert data["full_name"] == "Alice Wonderland"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data  # Ensure hashed password is never leaked


def test_register_duplicate_email(client):
    payload = {
        "email": "bob@example.com",
        "username": "bob1",
        "password": "password123",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    payload_dup = {
        "email": "bob@example.com",
        "username": "bob2",
        "password": "password123",
    }
    res2 = client.post("/api/v1/auth/register", json=payload_dup)
    assert res2.status_code == 400
    assert "email already exists" in res2.json()["detail"].lower()


def test_register_duplicate_username(client):
    payload = {
        "email": "charlie1@example.com",
        "username": "charlie",
        "password": "password123",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    payload_dup = {
        "email": "charlie2@example.com",
        "username": "charlie",
        "password": "password123",
    }
    res2 = client.post("/api/v1/auth/register", json=payload_dup)
    assert res2.status_code == 400
    assert "username already exists" in res2.json()["detail"].lower()


def test_register_password_too_short(client):
    payload = {
        "email": "short@example.com",
        "username": "shortpwd",
        "password": "short",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_and_token_flow(client):
    # 1. Register user
    reg_payload = {
        "email": "david@example.com",
        "username": "david",
        "password": "mypassword123",
        "full_name": "David Bowie",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login with email
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "david@example.com", "password": "mypassword123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 3. Access protected /me endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == "david"
    assert me_data["email"] == "david@example.com"

    # 4. Access protected without token -> 401
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    # 5. Refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_access_token = refresh_res.json()["access_token"]
    assert new_access_token != ""

    # 6. Access /me with new access token
    new_me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert new_me_res.status_code == 200


def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "eve@example.com",
            "username": "eve123",
            "password": "securepassword",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "eve@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_oauth2_form_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "frank@example.com",
            "username": "frank",
            "password": "password456",
        },
    )

    response = client.post(
        "/api/v1/auth/login/oauth2",
        data={"username": "frank", "password": "password456"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_change_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "grace@example.com",
            "username": "grace",
            "password": "oldPassword123",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "grace", "password": "oldPassword123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    change_res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": "oldPassword123", "new_password": "newPassword999"},
    )
    assert change_res.status_code == 200

    # Old password fails
    fail_login = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "grace", "password": "oldPassword123"},
    )
    assert fail_login.status_code == 401

    # New password works
    success_login = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "grace", "password": "newPassword999"},
    )
    assert success_login.status_code == 200
