import pytest

from app import create_app
from app.extensions import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "jwt-test-secret"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///:memory:"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = "redis://localhost:6379/15"


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "user@example.com",
            "password": "password123",
            "name": "Test User",
        },
    )

    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }
