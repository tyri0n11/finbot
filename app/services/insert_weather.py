from uuid import uuid4
from model.weather import WeatherData

def insert_weather(client, data: WeatherData):
    location = data.location
    current = data.current
    condition = current.condition

    client.insert(
        "weather_data",
        [
            (
                str(uuid4()),
                location.name,
                location.country,
                location.lat,
                location.lon,
                location.localtime,       # đã là datetime
                current.last_updated,     # đã là datetime
                current.temp_c,
                current.temp_f,
                current.is_day,
                condition.text,
                condition.code,
                current.wind_kph,
                current.humidity,
                current.pressure_mb,
                current.precip_mm,
                current.feelslike_c,
                current.uv,
            )
        ],
        column_names=[
            "id",
            "city",
            "country",
            "latitude",
            "longitude",
            "localtime",
            "last_updated",
            "temp_c",
            "temp_f",
            "is_day",
            "condition_text",
            "condition_code",
            "wind_kph",
            "humidity",
            "pressure_mb",
            "precip_mm",
            "feelslike_c",
            "uv",
        ],
    )
