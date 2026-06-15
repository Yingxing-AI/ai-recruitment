from app.api.routes.health import health


def test_health() -> None:
    assert health() == {"status": "ok"}
