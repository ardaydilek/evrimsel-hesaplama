def test_build_prod_app_wires_routes(monkeypatch):
    # SQLite + a never-contacted Redis URL: make_redis()/Queue() are lazy, so no
    # network is touched at construction. We only assert the app is wired.
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    from arena_core.server import build_prod_app
    app = build_prod_app()
    paths = {r.path for r in app.routes}
    assert {"/api/submissions", "/api/leaderboard", "/api/problem", "/api/presets"} <= paths


def test_build_prod_app_does_not_create_tables(monkeypatch):
    # Alembic owns the schema; the prod app must NOT create tables. Spy on the real
    # sink (Base.metadata.create_all) so this fails if create_all is reintroduced by
    # ANY path (a direct call or a re-added init_db import).
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    from unittest.mock import patch
    from arena_core.db import Base
    import arena_core.server as server
    with patch.object(Base.metadata, "create_all", autospec=True) as create_all:
        server.build_prod_app()
    assert not create_all.called
