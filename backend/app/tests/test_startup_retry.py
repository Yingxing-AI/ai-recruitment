from sqlalchemy.exc import OperationalError

from app import main


def test_wait_for_database_ready_retries_until_success(monkeypatch) -> None:
    attempts = {"count": 0}

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def execute(self, _query) -> None:
            return None

    class FakeEngine:
        def connect(self):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise OperationalError("SELECT 1", {}, Exception("db not ready"))
            return FakeConnection()

    monkeypatch.setattr(main, "engine", FakeEngine())
    monkeypatch.setattr(main.settings, "database_startup_max_attempts", 3)
    monkeypatch.setattr(main.settings, "database_startup_retry_delay_seconds", 0.0)
    monkeypatch.setattr(main.time, "sleep", lambda _seconds: None)

    main.wait_for_database_ready()

    assert attempts["count"] == 3


def test_wait_for_database_ready_raises_after_last_attempt(monkeypatch) -> None:
    class FakeEngine:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("db not ready"))

    monkeypatch.setattr(main, "engine", FakeEngine())
    monkeypatch.setattr(main.settings, "database_startup_max_attempts", 2)
    monkeypatch.setattr(main.settings, "database_startup_retry_delay_seconds", 0.0)
    monkeypatch.setattr(main.time, "sleep", lambda _seconds: None)

    try:
        main.wait_for_database_ready()
    except OperationalError:
        return

    raise AssertionError("wait_for_database_ready should raise after the final attempt")
