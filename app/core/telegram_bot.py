import httpx
from core.logger import get_logger


class TelegramBot:
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"{self.BASE_URL}{token}"
        self.logger = get_logger()
        self.logger.info("TelegramBot initialized")

    async def get_me(self):
        url = f"{self.base_url}/getMe"
        self.logger.debug(f"Calling getMe: {url}")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        self.logger.info(f"getMe response: {r.status_code}")
        return r.json()

    async def get_updates(self):
        url = f"{self.base_url}/getUpdates"
        self.logger.debug(f"Calling getUpdates: {url}")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        self.logger.info(f"getUpdates response: {r.status_code}")
        return r.json()

    async def send_message(self, chat_id: int, text: str, mode_html: bool = False):
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if mode_html:
            data["parse_mode"] = "HTML"

        self.logger.debug(f"Sending message: {data}")
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data)
        if r.is_success:
            self.logger.info(f"Message sent to chat_id={chat_id}")
        else:
            self.logger.error(f"Failed to send message: {r.text}")
        return r.json()

    async def set_webhook(self, url: str):
        api = f"{self.base_url}/setWebhook"
        self.logger.info(f"Setting webhook: {url}")
        async with httpx.AsyncClient() as client:
            r = await client.post(api, json={"url": url})
        if r.is_success:
            self.logger.info("Webhook set successfully")
        else:
            self.logger.error(f"Failed to set webhook: {r.text}")
        return r.json()

    async def delete_webhook(self):
        url = f"{self.base_url}/deleteWebhook"
        self.logger.info("Deleting webhook")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        self.logger.info(f"deleteWebhook response: {r.status_code}")
        return r.json()

    async def get_webhook_info(self):
        url = f"{self.base_url}/getWebhookInfo"
        self.logger.debug("Getting webhook info")
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        self.logger.info(f"Webhook info response: {r.status_code}")
        return r.json()
