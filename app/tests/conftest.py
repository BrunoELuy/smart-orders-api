import bcrypt
import pytest
from app import create_app
from app.infrastructure.database.db import db
from app.infrastructure.database.models import User


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():

        password_hash = bcrypt.generate_password_hash("123").decode("utf-8")

        user = User(
            email="test@email.com",
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return user


@pytest.fixture
def auth_token(client, test_user):

    login_data = {
        "email": "test@email.com",
        "password": "123"
    }

    response = client.post("/login", json=login_data)

    token = response.json["token"]

    return token


@pytest.fixture
def auth_headers(auth_token):

    return {
        "Authorization": f"Bearer {auth_token}"
    }
