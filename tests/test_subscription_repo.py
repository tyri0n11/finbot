"""Tests for SubscriptionRepository (PostgreSQL mocked)."""
import pytest
from unittest.mock import MagicMock, call
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from repo.subscription_repo import SubscriptionRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(mock_db):
    db, conn, cursor = mock_db
    return SubscriptionRepository(db), db, conn, cursor


# ---------------------------------------------------------------------------
# init_schema
# ---------------------------------------------------------------------------

def test_init_schema_executes_create_table(repo):
    r, db, conn, cursor = repo
    r.init_schema()
    cursor.execute.assert_called_once()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS user_subscriptions" in sql
    conn.commit.assert_called_once()


def test_init_schema_no_connection(mock_db):
    db, conn, cursor = mock_db
    db.get_postgres_connection.return_value = None
    r = SubscriptionRepository(db)
    r.init_schema()  # Should not raise
    cursor.execute.assert_not_called()


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------

def test_upsert_returns_subscription(repo):
    r, db, conn, cursor = repo
    cursor.fetchone.return_value = (1, 12345, "weather", "07:00", "daily", True, None, None, None)

    sub = r.upsert(12345, "weather", "07:00", "daily")

    assert sub is not None
    assert sub.chat_id == 12345
    assert sub.subscription_type == "weather"
    assert sub.scheduled_time == "07:00"
    conn.commit.assert_called_once()


def test_upsert_no_connection(mock_db):
    db, conn, cursor = mock_db
    db.get_postgres_connection.return_value = None
    r = SubscriptionRepository(db)
    sub = r.upsert(12345, "weather", "07:00", "daily")
    assert sub is None


# ---------------------------------------------------------------------------
# get_due_subscriptions
# ---------------------------------------------------------------------------

def test_get_due_subscriptions_returns_list(repo):
    r, db, conn, cursor = repo
    cursor.fetchall.return_value = [
        (1, 12345, "weather", "07:00", "daily", True, None, None, None),
        (2, 99999, "news",    "07:00", "daily", True, None, None, None),
    ]

    results = r.get_due_subscriptions("07:00", date.today())

    assert len(results) == 2
    assert results[0].subscription_type == "weather"
    assert results[1].subscription_type == "news"
    sql = cursor.execute.call_args[0][0]
    assert "scheduled_time = %s" in sql
    assert "last_sent_at" in sql


def test_get_due_subscriptions_empty(repo):
    r, db, conn, cursor = repo
    cursor.fetchall.return_value = []
    results = r.get_due_subscriptions("07:00", date.today())
    assert results == []


# ---------------------------------------------------------------------------
# update_last_sent
# ---------------------------------------------------------------------------

def test_update_last_sent(repo):
    r, db, conn, cursor = repo
    now = datetime(2026, 3, 1, 7, 0, 0)
    r.update_last_sent(1, now)
    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args[0]
    assert "last_sent_at" in sql
    assert params == (now, 1)
    conn.commit.assert_called_once()


# ---------------------------------------------------------------------------
# get_by_chat_id
# ---------------------------------------------------------------------------

def test_get_by_chat_id(repo):
    r, db, conn, cursor = repo
    cursor.fetchall.return_value = [
        (1, 12345, "weather",    "07:00", "daily", True, None, None, None),
        (2, 12345, "gold_price", "09:00", "daily", True, None, None, None),
    ]
    results = r.get_by_chat_id(12345)
    assert len(results) == 2
    assert all(s.chat_id == 12345 for s in results)


def test_get_by_chat_id_empty(repo):
    r, db, conn, cursor = repo
    cursor.fetchall.return_value = []
    results = r.get_by_chat_id(12345)
    assert results == []


# ---------------------------------------------------------------------------
# deactivate
# ---------------------------------------------------------------------------

def test_deactivate_returns_true_when_row_updated(repo):
    r, db, conn, cursor = repo
    cursor.rowcount = 1
    result = r.deactivate(12345, "weather")
    assert result is True
    conn.commit.assert_called_once()


def test_deactivate_returns_false_when_no_row(repo):
    r, db, conn, cursor = repo
    cursor.rowcount = 0
    result = r.deactivate(12345, "weather")
    assert result is False
