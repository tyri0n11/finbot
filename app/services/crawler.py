# import requests

# from fastapi import HTTPException
# from repo.weather import WeatherRepo

# from model.weather import parse_weather
# from core.database import Database
# from core.settings import Settings

# class CrawlerService:
#     def __init__(self):
#         self.api_key = Settings().WEATHER_API_KEY
#         self.base_url = Settings().CRAWL_BASE_URL
#         self.lang = "vi"
#         self.DB = Database()
#         self.weather_repo = WeatherRepo(self.DB.get_session())

#     def get_current_by_location(self, location: str):
#         url = f"{self.base_url}current.json"

#         params = {
#             "q": location,
#             "lang": self.lang,
#             "key": self.api_key
#         }
#         try:
#             response = requests.get(url, params=params)
#             response.raise_for_status()
#             weather_model = parse_weather(response.json())
#             self.weather_repo.insert_weather(weather_model)
            

#             return {
#                 "status_code": response.status_code,
#             }
#         except requests.exceptions.RequestException as e:
#             raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")