"""Databricks startup is read-only and cannot silently fall back to SQLite."""
import asyncio
from types import SimpleNamespace

import pytest

from backend import main
from backend.database import engine
from backend.models import Base


def run_startup():
    async def run():
        async with main.lifespan(main.app):
            pass
    asyncio.run(run())


def test_databricks_refuses_development_identity(monkeypatch):
    monkeypatch.setenv('DATABRICKS_APP_PORT', '8000')
    monkeypatch.setattr(main, 'get_settings', lambda: SimpleNamespace(dev_mode=True))
    with pytest.raises(RuntimeError, match='DEV_MODE'):
        run_startup()


def test_databricks_refuses_sqlite_fallback(monkeypatch):
    monkeypatch.setenv('DATABRICKS_APP_PORT', '8000')
    monkeypatch.setattr(main, 'get_settings', lambda: SimpleNamespace(dev_mode=False))
    with pytest.raises(RuntimeError, match='SQLite fallback is forbidden'):
        run_startup()


def test_databricks_requires_schema_without_creating_it(monkeypatch):
    monkeypatch.setenv('DATABRICKS_APP_PORT', '8000')
    monkeypatch.setattr(main, 'get_settings', lambda: SimpleNamespace(dev_mode=False))
    # The dialect contract is faked here; live PostgreSQL requires deployment validation.
    monkeypatch.setattr(main, '_current_schema', lambda connection: 'main')
    monkeypatch.setattr(main, 'engine', SimpleNamespace(dialect=SimpleNamespace(name='postgresql'), connect=engine.connect))
    Base.metadata.tables['integration_framework_profiles'].drop(engine)
    monkeypatch.setattr(Base.metadata, 'create_all', lambda *a, **kw: pytest.fail('Production attempted DDL'))
    with pytest.raises(RuntimeError, match='migrate_framework.py'):
        run_startup()


def test_databricks_complete_schema_is_read_only(monkeypatch):
    monkeypatch.setenv('DATABRICKS_APP_PORT', '8000')
    monkeypatch.setattr(main, 'get_settings', lambda: SimpleNamespace(dev_mode=False))
    monkeypatch.setattr(main, '_current_schema', lambda connection: 'main')
    monkeypatch.setattr(main, 'engine', SimpleNamespace(dialect=SimpleNamespace(name='postgresql'), connect=engine.connect))
    monkeypatch.setattr(Base.metadata, 'create_all', lambda *a, **kw: pytest.fail('Production attempted DDL'))
    run_startup()
