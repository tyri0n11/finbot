"""
Shared pytest fixtures.

PYTHONPATH must include the 'app/' directory for all imports to resolve.
Set via pytest.ini: pythonpath = app
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db():
    """A mock Database object with a working postgres pool."""
    db = MagicMock()
    conn = MagicMock()
    cursor = MagicMock()

    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    db.get_postgres_connection.return_value = conn
    db.return_postgres_connection.return_value = None
    return db, conn, cursor


@pytest.fixture
def mock_bot(monkeypatch):
    """Patch TelegramBot.send_message to avoid real HTTP calls."""
    send = AsyncMock(return_value={"ok": True})
    monkeypatch.setattr("core.telegram_bot.TelegramBot.send_message", send)
    return send
