import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from core.settings import settings
from core.database import Database
from core.telegram_bot import TelegramBot
from core.logger import get_logger
from repo.subscription_repo import SubscriptionRepository
from services.weather import WeatherService
from services.news import NewsService
from services.gold_price import GoldPriceService

TAG = "NotificationScheduler"


class NotificationScheduler:
    def __init__(self, db: Database):
        self.db = db
        self.repo = SubscriptionRepository(db)
        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        self.weather_svc = WeatherService()
        self.news_svc = NewsService()
        self.gold_svc = GoldPriceService()
        self.logger = get_logger()

    async def run(self) -> None:
        self.logger.info(f"[{TAG}] Scheduler started, polling every 60s")
        while True:
            try:
                await self._check_and_send()
            except Exception as e:
                self.logger.error(f"[{TAG}] Unexpected error: {e}", exc_info=True)
            await asyncio.sleep(60)

    async def _check_and_send(self) -> None:
        tz = ZoneInfo(settings.TIMEZONE)
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        today = now.date()

        subs = self.repo.get_due_subscriptions(current_time, today)
        if not subs:
            return

        self.logger.info(f"[{TAG}] {len(subs)} subscription(s) due at {current_time}")
        for sub in subs:
            try:
                content = await self._fetch_content(sub.subscription_type)
                await self.bot.send_message(sub.chat_id, content, mode_html=True)
                self.repo.update_last_sent(sub.id, now)
                self.logger.info(f"[{TAG}] Sent {sub.subscription_type} to chat {sub.chat_id}")
            except Exception as e:
                self.logger.error(f"[{TAG}] Failed to send {sub.subscription_type} to {sub.chat_id}: {e}")

    async def _fetch_content(self, sub_type: str) -> str:
        if sub_type == "weather":
            return await self.weather_svc.get_weather()
        elif sub_type == "news":
            return await self.news_svc.get_news()
        elif sub_type == "gold_price":
            return await self.gold_svc.get_gold_price()
        return f"⚠️ Unknown subscription type: {sub_type}"
