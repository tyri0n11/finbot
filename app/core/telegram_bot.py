import httpx
from typing import List, Dict, Any, Optional
from core.logger import get_logger


class TelegramBot:
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"{self.BASE_URL}{token}"
        self.logger = get_logger()
        self.logger.info("TelegramBot initialized")

    async def get_me(self):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/getMe")
        return r.json()

    async def get_updates(self):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/getUpdates")
        return r.json()

    async def send_message(self, chat_id: int, text: str,
                           mode_html: bool = False,
                           reply_markup: Optional[Dict] = None):
        data: Dict[str, Any] = {"chat_id": chat_id, "text": text}
        if mode_html:
            data["parse_mode"] = "HTML"
        if reply_markup:
            data["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/sendMessage", json=data)
        if r.is_success:
            self.logger.info(f"Message sent to chat_id={chat_id}")
        else:
            self.logger.error(f"Failed to send message: {r.text}")
        return r.json()

    async def edit_message_text(self, chat_id: int, message_id: int, text: str,
                                mode_html: bool = False,
                                reply_markup: Optional[Dict] = None):
        """Edit an existing message (used to update inline keyboards)."""
        data: Dict[str, Any] = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if mode_html:
            data["parse_mode"] = "HTML"
        if reply_markup:
            data["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/editMessageText", json=data)
        if not r.is_success:
            self.logger.error(f"Failed to edit message: {r.text}")
        return r.json()

    async def answer_callback_query(self, callback_query_id: str, text: str = ""):
        """Acknowledge a callback query (removes loading spinner on button)."""
        data = {"callback_query_id": callback_query_id, "text": text}
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/answerCallbackQuery", json=data)
        return r.json()

    async def set_webhook(self, url: str):
        self.logger.info(f"Setting webhook: {url}")
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.base_url}/setWebhook", json={"url": url})
        if r.is_success:
            self.logger.info("Webhook set successfully")
        else:
            self.logger.error(f"Failed to set webhook: {r.text}")
        return r.json()

    async def delete_webhook(self):
        self.logger.info("Deleting webhook")
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/deleteWebhook")
        self.logger.info(f"deleteWebhook response: {r.status_code}")
        return r.json()

    async def get_webhook_info(self):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/getWebhookInfo")
        return r.json()
