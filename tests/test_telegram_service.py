"""Tests for TelegramService command routing."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from services.telegram import TelegramService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_message(text: str, chat_id: int = 12345) -> dict:
    return {"chat": {"id": chat_id}, "text": text}


async def _process(service, text, chat_id=12345):
    return await service.process_message(_make_message(text, chat_id))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service(mock_bot):
    """TelegramService with mocked bot and no DB (repo returns None)."""
    svc = TelegramService()
    svc._repo = None
    svc._db = None
    return svc


@pytest.fixture
def service_with_repo(mock_bot):
    """TelegramService with a mocked SubscriptionRepository."""
    repo = MagicMock()
    svc = TelegramService()
    svc._repo = repo
    svc._db = None
    return svc, repo


# ---------------------------------------------------------------------------
# Non-command messages
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_echo_non_command(service, mock_bot):
    result = await _process(service, "hello world")
    assert result is True
    mock_bot.assert_called_once()
    call_args = mock_bot.call_args[0]
    assert "Echo: hello world" in call_args[1]


@pytest.mark.asyncio
async def test_empty_message_returns_false(service):
    result = await service.process_message({"chat": {"id": 1}, "text": ""})
    assert result is False


# ---------------------------------------------------------------------------
# /help
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_help_command(service, mock_bot):
    result = await _process(service, "/help")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "FinBot" in text
    assert "/set-weather" in text


# ---------------------------------------------------------------------------
# /set-* commands
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_weather_no_db(service, mock_bot):
    """When repo is None (no DB), send the 'not ready' message."""
    result = await _process(service, "/set-weather 7am daily")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "sẵn sàng" in text


@pytest.mark.asyncio
async def test_set_weather_with_repo(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    from model.subscription import UserSubscription
    repo.upsert.return_value = UserSubscription(
        id=1, chat_id=12345, subscription_type="weather",
        scheduled_time="07:00", frequency="daily"
    )
    result = await _process(svc, "/set-weather 7am daily")
    assert result is True
    repo.upsert.assert_called_once_with(12345, "weather", "07:00", "daily")
    text = mock_bot.call_args[0][1]
    assert "07:00" in text


@pytest.mark.asyncio
async def test_set_invalid_time(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    result = await _process(svc, "/set-weather badtime daily")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "không hợp lệ" in text.lower() or "invalid" in text.lower() or "Định dạng" in text


@pytest.mark.asyncio
async def test_set_missing_time(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    result = await _process(svc, "/set-news")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "Thiếu" in text or "thiếu" in text


# ---------------------------------------------------------------------------
# /unset-* commands
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unset_weather_active(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    repo.deactivate.return_value = True
    result = await _process(svc, "/unset-weather")
    assert result is True
    repo.deactivate.assert_called_once_with(12345, "weather")
    text = mock_bot.call_args[0][1]
    assert "Đã hủy" in text


@pytest.mark.asyncio
async def test_unset_weather_not_subscribed(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    repo.deactivate.return_value = False
    result = await _process(svc, "/unset-weather")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "không có" in text.lower() or "Bạn không" in text


# ---------------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_status_no_subscriptions(service_with_repo, mock_bot):
    svc, repo = service_with_repo
    repo.get_by_chat_id.return_value = []
    result = await _process(svc, "/status")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "chưa có" in text.lower() or "không có" in text.lower()


@pytest.mark.asyncio
async def test_status_with_subscriptions(service_with_repo, mock_bot):
    from model.subscription import UserSubscription
    svc, repo = service_with_repo
    repo.get_by_chat_id.return_value = [
        UserSubscription(id=1, chat_id=12345, subscription_type="weather",
                         scheduled_time="07:00", frequency="daily"),
        UserSubscription(id=2, chat_id=12345, subscription_type="news",
                         scheduled_time="08:30", frequency="daily"),
    ]
    result = await _process(svc, "/status")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "07:00" in text
    assert "08:30" in text


# ---------------------------------------------------------------------------
# Unknown command
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unknown_command(service, mock_bot):
    result = await _process(service, "/foobar")
    assert result is True
    text = mock_bot.call_args[0][1]
    assert "không hợp lệ" in text.lower() or "Lệnh" in text
