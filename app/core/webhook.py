import httpx
import asyncio
import xml.etree.ElementTree as ET
from core.settings import settings
from core.telegram_bot import TelegramBot
from core.logger import get_logger


TAG = "Webhook"
class WebhookManager:
    def __init__(self):
        self.logger = get_logger()
        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        self.current_url = None

    async def fetch_ngrok_url(self) -> str | None:
        async with httpx.AsyncClient() as client:
            r = await client.get(settings.NGROK_API, headers={"Accept": "application/xml"})
            root = ET.fromstring(r.text)

            for tunnel in root.findall(".//Tunnels"):
                public_url = tunnel.find("PublicURL")
                if public_url is not None and public_url.text.startswith("https://"):
                    return public_url.text
        return None

    async def monitor_webhook(self):
        while True:
            try:
                url = await self.fetch_ngrok_url()
                if url and url != self.current_url:
                    self.logger.info(f"[{TAG}] New ngrok URL: {url}")
                    await self.bot.delete_webhook()
                    resp = await self.bot.set_webhook(url+f"/webhook")
                    self.logger.info(f"[{TAG}] Webhook set result: {resp}")
                    self.current_url = url
            except Exception as e:
                self.logger.error(f"[{TAG}] Error: {e}", exc_info=True)
            await asyncio.sleep(10)

