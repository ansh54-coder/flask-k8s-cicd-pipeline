def test_register(client):
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "john@example.com",
            "password": "password123",
            "name": "John",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["user"]["email"] == "john@example.com"
    assert "access_token" in data


def test_login(client):
    client.post(
        "/api/v1/users/register",
        json={
            "email": "john@example.com",
            "password": "password123",
            "name": "John",
        },
    )

    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "john@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_me(client, auth_headers):
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["email"] == "user@example.com"
