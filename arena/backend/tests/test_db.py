from arena_core.db import Base, make_engine


def test_metadata_has_naming_convention():
    nc = Base.metadata.naming_convention
    assert nc["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    assert nc["pk"] == "pk_%(table_name)s"


def test_sqlite_engine_has_no_pre_ping():
    engine = make_engine("sqlite:///:memory:")
    assert engine.pool._pre_ping is False


def test_postgres_engine_enables_pre_ping(monkeypatch):
    # Capture the kwargs passed to create_engine WITHOUT importing the psycopg
    # driver (SQLAlchemy 2.0 imports the DBAPI eagerly in create_engine; psycopg
    # isn't installed until Task 4). Returning a sqlite engine keeps it driver-free.
    import arena_core.db as db
    from sqlalchemy import create_engine as real_create_engine
    captured = {}

    def fake_create_engine(url, **kwargs):
        captured.update(kwargs)
        return real_create_engine("sqlite:///:memory:")

    monkeypatch.setattr(db, "create_engine", fake_create_engine)
    db.make_engine("postgresql+psycopg://u:p@localhost/db")
    assert captured.get("pool_pre_ping") is True
