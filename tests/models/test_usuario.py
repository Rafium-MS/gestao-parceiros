import pytest
from werkzeug.security import check_password_hash

from database.db_manager import DatabaseManager
from models.usuario import Usuario


@pytest.fixture
def db_manager(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "admin")
    db_path = tmp_path / "usuarios.db"
    manager = DatabaseManager(str(db_path))
    manager.setup_database()
    yield manager
    manager.close_connection()


def test_salvar_usuario_armazenando_hash(db_manager):
    usuario = Usuario(db_manager)
    usuario.username = "novo_usuario"
    usuario.role_id = 1
    usuario.set_password("segredo")

    assert usuario.salvar()

    db_manager.execute(
        "SELECT password FROM users WHERE username=?",
        ("novo_usuario",),
    )
    senha_armazenada = db_manager.fetchone()[0]
    assert senha_armazenada != "segredo"
    assert check_password_hash(senha_armazenada, "segredo")


def test_autenticacao_bem_sucedida(db_manager):
    usuario = Usuario(db_manager)
    usuario.username = "autenticacao"
    usuario.role_id = 1
    usuario.set_password("senha_segura")
    assert usuario.salvar()

    autenticado, usuario_retornado = Usuario.autenticar(
        db_manager, "autenticacao", "senha_segura"
    )
    assert autenticado is True
    assert usuario_retornado is not None
    assert usuario_retornado.username == "autenticacao"


def test_autenticacao_falha_senha_incorreta(db_manager):
    usuario = Usuario(db_manager)
    usuario.username = "falha"
    usuario.role_id = 1
    usuario.set_password("senha_correta")
    assert usuario.salvar()

    autenticado, usuario_retornado = Usuario.autenticar(
        db_manager, "falha", "senha_errada"
    )
    assert autenticado is False
    assert usuario_retornado is None


def test_autenticacao_migra_senha_plana(db_manager):
    db_manager.execute(
        "INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)",
        ("legacy", "senha_antiga", 1),
    )
    db_manager.commit()

    autenticado, usuario_retornado = Usuario.autenticar(
        db_manager, "legacy", "senha_antiga"
    )
    assert autenticado is True
    assert usuario_retornado is not None

    db_manager.execute(
        "SELECT password FROM users WHERE username=?",
        ("legacy",),
    )
    senha_armazenada = db_manager.fetchone()[0]
    assert senha_armazenada != "senha_antiga"
    assert check_password_hash(senha_armazenada, "senha_antiga")
