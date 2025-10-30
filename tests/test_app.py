import io
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import app
from models import User, Partner, Brand, Store


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


def _api_login(client, username="admin", password="admin"):
    response = client.post(
        "/api/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response


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
        assert create_response.get_json()["data"]["id"]

        duplicate_response = client.post(
            "/api/users",
            json={"username": "operador", "password": "outra123", "role": "operator"},
        )

    assert duplicate_response.status_code == 400
    assert duplicate_response.get_json()["error"]["message"] == "username já existe"

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


def test_api_login_and_partner_flow(tmp_path, monkeypatch):
    flask_app, _ = _create_test_app(tmp_path, monkeypatch)

    with flask_app.test_client() as client:
        login_response = client.post(
            "/api/login",
            json={"username": "admin", "password": "admin"},
        )

        assert login_response.status_code == 200
        data = login_response.get_json()["data"]
        assert data["user"]["username"] == "admin"

        create_partner_response = client.post(
            "/api/partners",
            json={
                "cidade": "São Paulo",
                "estado": "SP",
                "parceiro": "Distribuidora Azul",
                "cnpj_cpf": "12.345.678/0001-99",
                "telefone": "11999999999",
                "email": "contato@azul.com",
            },
        )

        assert create_partner_response.status_code == 201
        partner_payload = create_partner_response.get_json()["data"]
        assert partner_payload["parceiro"] == "Distribuidora Azul"

        partners_response = client.get("/api/partners")
        assert partners_response.status_code == 200
        partners = partners_response.get_json()["data"]
        assert any(partner["id"] == partner_payload["id"] for partner in partners)


def test_partner_import_creates_and_updates(tmp_path, monkeypatch):
    flask_app, db_path = _create_test_app(tmp_path, monkeypatch)

    Session = _get_session(db_path)

    with flask_app.test_client() as client:
        _api_login(client)

        csv_content = (
            "Parceiro,Documento,Cidade,UF,Telefone,Email,Dia de Pagamento,CX Copo\n"
            'Distribuidora Azul,"12.345.678/0001-99","São Paulo",sp,"(11) 99999-9999",contato@azul.com,15,"1.234,50"\n'
        )
        response = client.post(
            "/api/partners/import",
            data={"file": (io.BytesIO(csv_content.encode("utf-8")), "partners.csv")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        summary = response.get_json()["data"]
        assert summary == {
            "total": 1,
            "created": 1,
            "updated": 0,
            "skipped": 0,
            "error_count": 0,
            "errors": [],
        }

        with Session() as session:
            partner = session.query(Partner).one()
            assert partner.cidade == "São Paulo"
            assert partner.estado == "SP"
            assert partner.cnpj_cpf == "12345678000199"
            assert partner.cx_copo == 1234.50

        update_content = (
            "Parceiro,Documento,Cidade,UF,Telefone,Email,Dia de Pagamento,CX Copo\n"
            'Distribuidora Azul,"12.345.678/0001-99",Campinas,SP,"(11) 99999-9999",contato@azul.com,20,"2,50"\n'
        )
        update_response = client.post(
            "/api/partners/import",
            data={"file": (io.BytesIO(update_content.encode("utf-8")), "partners.csv")},
            content_type="multipart/form-data",
        )

        assert update_response.status_code == 200
        update_summary = update_response.get_json()["data"]
        assert update_summary == {
            "total": 1,
            "created": 0,
            "updated": 1,
            "skipped": 0,
            "error_count": 0,
            "errors": [],
        }

        with Session() as session:
            partner = session.query(Partner).one()
            assert partner.cidade == "Campinas"
            assert partner.dia_pagamento == 20
            assert partner.cx_copo == 2.5


def test_brand_store_import_creates_and_updates(tmp_path, monkeypatch):
    flask_app, db_path = _create_test_app(tmp_path, monkeypatch)

    Session = _get_session(db_path)

    with flask_app.test_client() as client:
        _api_login(client)

        csv_content = (
            "Marca,Código Marca,Loja,Local de Entrega,Município,UF,Valor 20L,Valor 10L\n"
            'Super Agua,BR001,Loja Centro,Central,Uberlândia,mg,"15,90","7,50"\n'
        )
        response = client.post(
            "/api/brands/import",
            data={"file": (io.BytesIO(csv_content.encode("utf-8")), "brands.csv")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        summary = response.get_json()["data"]
        assert summary == {
            "total": 1,
            "created_brands": 1,
            "updated_brands": 0,
            "created_stores": 1,
            "updated_stores": 0,
            "skipped": 0,
            "error_count": 0,
            "errors": [],
        }

        with Session() as session:
            brand = session.query(Brand).one()
            store = session.query(Store).one()
            assert brand.marca == "Super Agua"
            assert brand.cod_disagua == "BR001"
            assert store.loja == "Loja Centro"
            assert store.uf == "MG"
            assert store.valor_20l == 15.90
            assert store.valor_10l == 7.50

        update_content = (
            "Marca,Código Marca,Loja,Local de Entrega,Município,UF,Valor 20L,Valor 10L\n"
            'Super Agua,BR-001,Loja Centro,Central,Uberlândia,MG,"16,10","8"\n'
        )
        update_response = client.post(
            "/api/brands/import",
            data={"file": (io.BytesIO(update_content.encode("utf-8")), "brands.csv")},
            content_type="multipart/form-data",
        )

        assert update_response.status_code == 200
        update_summary = update_response.get_json()["data"]
        assert update_summary == {
            "total": 1,
            "created_brands": 0,
            "updated_brands": 1,
            "created_stores": 0,
            "updated_stores": 1,
            "skipped": 0,
            "error_count": 0,
            "errors": [],
        }

        with Session() as session:
            brand = session.query(Brand).one()
            store = session.query(Store).one()
            assert brand.cod_disagua == "BR-001"
            assert store.valor_20l == 16.10
            assert store.valor_10l == 8.0
