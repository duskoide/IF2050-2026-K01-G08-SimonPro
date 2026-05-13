from types import SimpleNamespace
import importlib

auth_module = importlib.import_module("src.services.AuthService")


class FakeCursor:
    def __init__(self):
        self.executed = []

    def execute(self, sql, params):
        self.executed.append((sql, params))

    def close(self):
        return None


class FakeConnection:
    def __init__(self):
        self.cursor_obj = FakeCursor()
        self.committed = 0

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed += 1


class FakeDb:
    def __init__(self):
        self.connection = FakeConnection()


class FakeSession:
    def __init__(self):
        self.session_id = "sess-1"
        self.login_time = "2026-05-13 10:00:00"
        self.is_active = True
        self.logged_in_user = None
        self.invalidated = False

    def create_session(self, user):
        self.logged_in_user = user

    def invalidate(self):
        self.is_active = False
        self.invalidated = True


def test_validate_credentials_sukses(monkeypatch):
    fake_db = FakeDb()
    monkeypatch.setattr(auth_module, "get_db", lambda: fake_db)
    monkeypatch.setattr(auth_module, "Session", FakeSession)
    monkeypatch.setattr(auth_module, "UserDataLocal", lambda: SimpleNamespace(find_by_username=lambda username: None))

    service = auth_module.AuthService()
    service.user_data_local = SimpleNamespace(
        find_by_username=lambda username: SimpleNamespace(
            user_id=7,
            username="admin",
            password="admin123",
        )
    )

    result = service.validate_credentials("admin", "admin123")

    assert result is True
    assert service.is_authenticated() is True
    assert fake_db.connection.committed == 1
    assert len(fake_db.connection.cursor_obj.executed) == 1


def test_validate_credentials_gagal_password_salah(monkeypatch):
    monkeypatch.setattr(auth_module, "Session", FakeSession)
    monkeypatch.setattr(auth_module, "UserDataLocal", lambda: SimpleNamespace(find_by_username=lambda username: None))
    service = auth_module.AuthService()
    service.user_data_local = SimpleNamespace(
        find_by_username=lambda username: SimpleNamespace(
            user_id=7,
            username="admin",
            password="admin123",
        )
    )

    result = service.validate_credentials("admin", "wrong")

    assert result is False
    assert service.current_session is None


def test_logout_mengakhiri_sesi(monkeypatch):
    fake_db = FakeDb()
    monkeypatch.setattr(auth_module, "get_db", lambda: fake_db)
    monkeypatch.setattr(auth_module, "Session", FakeSession)
    monkeypatch.setattr(auth_module, "UserDataLocal", lambda: SimpleNamespace(find_by_username=lambda username: None))

    service = auth_module.AuthService()
    service.current_session = FakeSession()

    service.logout("sess-1")

    assert service.current_session is None
    assert fake_db.connection.committed == 1
    assert len(fake_db.connection.cursor_obj.executed) == 1
