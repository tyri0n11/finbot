import httpx
from core.settings import settings
from core.logger import get_logger

TAG = "NewsService"


class NewsService:
    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self):
        self.logger = get_logger()

    async def get_news(self) -> str:
        if not settings.NEWS_API_KEY:
            return "⚠️ News service not configured (missing NEWS_API_KEY)."

        params = {
            "country": "vn",
            "apiKey": settings.NEWS_API_KEY,
            "pageSize": 5,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(self.BASE_URL, params=params)

            if not r.is_success:
                self.logger.error(f"[{TAG}] API error {r.status_code}: {r.text}")
                return "⚠️ Không thể lấy tin tức."

            data = r.json()
            articles = data.get("articles", [])

            # Fallback: if no results with country=vn, try language=vi
            if not articles:
                params = {"language": "vi", "apiKey": settings.NEWS_API_KEY, "pageSize": 5}
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.get(self.BASE_URL, params=params)
                data = r.json()
                articles = data.get("articles", [])

            if not articles:
                return "📰 Không có tin tức mới."

            lines = ["📰 <b>Tin tức nổi bật hôm nay</b>\n"]
            for i, article in enumerate(articles[:5], 1):
                title = article.get("title", "Không có tiêu đề")
                url = article.get("url", "")
                lines.append(f"{i}. <a href=\"{url}\">{title}</a>")

            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"[{TAG}] Failed to fetch news: {e}")
            return "⚠️ Lỗi khi lấy tin tức."
