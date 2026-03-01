import httpx
from core.settings import settings
from core.logger import get_logger

TAG = "WeatherService"


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        self.logger = get_logger()

    async def get_weather(self) -> str:
        if not settings.OPENWEATHER_API_KEY:
            return "⚠️ Weather service not configured (missing OPENWEATHER_API_KEY)."

        params = {
            "q": settings.WEATHER_CITY,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "vi",
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(self.BASE_URL, params=params)
            if not r.is_success:
                self.logger.error(f"[{TAG}] API error {r.status_code}: {r.text}")
                return "⚠️ Không thể lấy dữ liệu thời tiết."

            data = r.json()
            city = data.get("name", settings.WEATHER_CITY)
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"].capitalize()
            wind_speed = data["wind"]["speed"]

            return (
                f"🌤 <b>Thời tiết {city}</b>\n"
                f"🌡 Nhiệt độ: <b>{temp:.1f}°C</b> (cảm giác {feels_like:.1f}°C)\n"
                f"☁️ Trời: {description}\n"
                f"💧 Độ ẩm: {humidity}%\n"
                f"💨 Gió: {wind_speed} m/s"
            )
        except Exception as e:
            self.logger.error(f"[{TAG}] Failed to fetch weather: {e}")
            return "⚠️ Lỗi khi lấy dữ liệu thời tiết."
