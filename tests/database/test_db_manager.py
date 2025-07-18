from database.db_manager import DatabaseManager


def test_setup_database(tmp_path):
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(str(db_path))
    manager.setup_database()
    manager.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='parceiros'"
    )
    assert manager.fetchone() == ("parceiros",)
    manager.close_connection()