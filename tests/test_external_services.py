"""Tests for WeatherService, NewsService, GoldPriceService (httpx mocked)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(status_code=200, json_data=None, text=""):
    resp = MagicMock()
    resp.is_success = status_code < 400
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text
    return resp


def _async_client_ctx(response):
    """Returns a context manager mock that yields a client returning `response`."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


# ---------------------------------------------------------------------------
# WeatherService
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_weather_no_api_key():
    from services.weather import WeatherService
    with patch("services.weather.settings") as mock_settings:
        mock_settings.OPENWEATHER_API_KEY = ""
        mock_settings.WEATHER_CITY = "Ho Chi Minh City"
        svc = WeatherService()
        result = await svc.get_weather()
    assert "not configured" in result or "OPENWEATHER_API_KEY" in result


@pytest.mark.asyncio
async def test_weather_success():
    from services.weather import WeatherService
    data = {
        "name": "Ho Chi Minh City",
        "main": {"temp": 32.5, "feels_like": 36.0, "humidity": 75},
        "weather": [{"description": "mây rải rác"}],
        "wind": {"speed": 3.5},
    }
    resp = _mock_response(json_data=data)
    ctx = _async_client_ctx(resp)

    with patch("services.weather.settings") as mock_settings, \
         patch("httpx.AsyncClient", return_value=ctx):
        mock_settings.OPENWEATHER_API_KEY = "test_key"
        mock_settings.WEATHER_CITY = "Ho Chi Minh City"
        svc = WeatherService()
        result = await svc.get_weather()

    assert "32.5" in result
    assert "Ho Chi Minh City" in result
    assert "75" in result


@pytest.mark.asyncio
async def test_weather_api_error():
    from services.weather import WeatherService
    resp = _mock_response(status_code=401, text="Unauthorized")
    ctx = _async_client_ctx(resp)

    with patch("services.weather.settings") as mock_settings, \
         patch("httpx.AsyncClient", return_value=ctx):
        mock_settings.OPENWEATHER_API_KEY = "bad_key"
        mock_settings.WEATHER_CITY = "Ho Chi Minh City"
        svc = WeatherService()
        result = await svc.get_weather()

    assert "⚠️" in result


# ---------------------------------------------------------------------------
# NewsService
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_news_no_api_key():
    from services.news import NewsService
    with patch("services.news.settings") as mock_settings:
        mock_settings.NEWS_API_KEY = ""
        svc = NewsService()
        result = await svc.get_news()
    assert "not configured" in result or "NEWS_API_KEY" in result


@pytest.mark.asyncio
async def test_news_success():
    from services.news import NewsService
    data = {
        "articles": [
            {"title": "Headline 1", "url": "https://example.com/1"},
            {"title": "Headline 2", "url": "https://example.com/2"},
        ]
    }
    resp = _mock_response(json_data=data)
    ctx = _async_client_ctx(resp)

    with patch("services.news.settings") as mock_settings, \
         patch("httpx.AsyncClient", return_value=ctx):
        mock_settings.NEWS_API_KEY = "test_key"
        svc = NewsService()
        result = await svc.get_news()

    assert "Headline 1" in result
    assert "Headline 2" in result


@pytest.mark.asyncio
async def test_news_empty_articles():
    from services.news import NewsService
    resp = _mock_response(json_data={"articles": []})
    ctx = _async_client_ctx(resp)

    # Both calls return empty
    client = AsyncMock()
    client.get = AsyncMock(return_value=resp)
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("services.news.settings") as mock_settings, \
         patch("httpx.AsyncClient", return_value=ctx):
        mock_settings.NEWS_API_KEY = "test_key"
        svc = NewsService()
        result = await svc.get_news()

    assert "không có" in result.lower() or "Không có" in result


# ---------------------------------------------------------------------------
# GoldPriceService
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_gold_price_success():
    from services.gold_price import GoldPriceService
    data = [
        {"kieu": "SJC 1 lượng", "mua": 8200000, "ban": 8250000},
    ]
    resp = _mock_response(json_data=data)
    ctx = _async_client_ctx(resp)

    with patch("httpx.AsyncClient", return_value=ctx):
        svc = GoldPriceService()
        result = await svc.get_gold_price()

    assert "8.200.000" in result or "8200000" in result or "8.200" in result
    assert "Mua" in result or "mua" in result.lower()


@pytest.mark.asyncio
async def test_gold_price_api_error():
    from services.gold_price import GoldPriceService
    resp = _mock_response(status_code=500, text="Server Error")
    ctx = _async_client_ctx(resp)

    with patch("httpx.AsyncClient", return_value=ctx):
        svc = GoldPriceService()
        result = await svc.get_gold_price()

    assert "⚠️" in result
