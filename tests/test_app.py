import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import app
from models import User


def _create_test_app(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(app, "DB_PATH", str(db_path))
    monkeypatch.setattr(app, "UPLOAD_DIR", str(upload_dir))
    os.makedirs(upload_dir, exist_ok=True)

    flask_app = app.create_app()
    flask_app.config["TESTING"] = True
    return flask_app, db_path


def _get_session(db_path):
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    return sessionmaker(bind=engine, future=True)


def test_login_creates_admin_user(tmp_path, monkeypatch):
    flask_app, db_path = _create_test_app(tmp_path, monkeypatch)

    with flask_app.test_client() as client:
        response = client.post("/login", data={"username": "admin", "password": "admin"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    Session = _get_session(db_path)
    with Session() as session:
        user = session.query(User).filter_by(username="admin").one()
        assert user.role == "admin"
        assert user.password_hash != "admin"


def test_account_update_rejects_short_password(tmp_path, monkeypatch):
    flask_app, _ = _create_test_app(tmp_path, monkeypatch)

    with flask_app.test_client() as client:
        login_response = client.post("/login", data={"username": "admin", "password": "admin"})
        assert login_response.status_code == 302

        response = client.post(
            "/account",
            data={
                "current_password": "admin",
                "new_password": "123",
                "confirm_password": "123",
            },
        )

    assert response.status_code == 200
    assert "A nova senha deve ter ao menos 6 caracteres." in response.get_data(as_text=True)


def test_account_update_requires_matching_confirmation(tmp_path, monkeypatch):
    flask_app, _ = _create_test_app(tmp_path, monkeypatch)

    with flask_app.test_client() as client:
        login_response = client.post("/login", data={"username": "admin", "password": "admin"})
        assert login_response.status_code == 302

        response = client.post(
            "/account",
            data={
                "current_password": "admin",
                "new_password": "novasenha",
                "confirm_password": "diferente",
            },
        )

    assert response.status_code == 200
    assert "A confirmação de senha não confere." in response.get_data(as_text=True)


def test_duplicate_username_is_rejected(tmp_path, monkeypatch):
    flask_app, db_path = _create_test_app(tmp_path, monkeypatch)

    with flask_app.test_client() as client:
        login_response = client.post("/login", data={"username": "admin", "password": "admin"})
        assert login_response.status_code == 302

        create_response = client.post(
            "/api/users",
            json={"username": "operador", "password": "secreta", "role": "operator"},
        )
        assert create_response.status_code == 201

        duplicate_response = client.post(
            "/api/users",
            json={"username": "operador", "password": "outra123", "role": "operator"},
        )

    assert duplicate_response.status_code == 400
    assert duplicate_response.get_json()["error"] == "username já existe"

    Session = _get_session(db_path)
    with Session() as session:
        users = session.query(User).filter_by(username="operador").all()
        assert len(users) == 1


def test_non_admin_cannot_access_user_listing(tmp_path, monkeypatch):
    flask_app, db_path = _create_test_app(tmp_path, monkeypatch)
    Session = _get_session(db_path)

    from werkzeug.security import generate_password_hash

    with Session() as session:
        operator = User(
            username="operador",
            password_hash=generate_password_hash("segredo"),
            role="operator",
        )
        session.add(operator)
        session.commit()

    with flask_app.test_client() as client:
        login_response = client.post(
            "/login",
            data={"username": "operador", "password": "segredo"},
            follow_redirects=False,
        )
        assert login_response.status_code == 302

        response = client.get("/api/users")

    assert response.status_code == 403
