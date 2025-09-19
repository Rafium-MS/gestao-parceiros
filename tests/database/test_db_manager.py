from database.db_manager import DatabaseManager
from werkzeug.security import check_password_hash


def test_setup_database(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "senha_teste")
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(str(db_path))
    manager.setup_database()
    manager.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='parceiros'"
    )
    assert manager.fetchone() == ("parceiros",)
    manager.execute("SELECT password FROM users WHERE username=?", ("admin",))
    senha_hash = manager.fetchone()[0]
    assert senha_hash != "senha_teste"
    assert check_password_hash(senha_hash, "senha_teste")
    manager.close_connection()