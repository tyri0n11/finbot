import re
from typing import Dict, Any, Optional
from core.telegram_bot import TelegramBot
from core.settings import settings
from core.logger import get_logger
from core.keyboards import (
    MAIN_MENU_TEXT, MAIN_MENU_KEYBOARD,
    time_picker_keyboard, time_picker_text,
    status_keyboard,
)

TAG = "Telegram_Service"

TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{2}))?(am|pm)?$", re.IGNORECASE)

SUB_COMMANDS = {
    "set-weather": "weather",
    "set-news": "news",
    "set-gold-price": "gold_price",
}

UNSET_COMMANDS = {
    "unset-weather": "weather",
    "unset-news": "news",
    "unset-gold-price": "gold_price",
}


def parse_time(token: str) -> Optional[str]:
    """Parse a time token into 'HH:MM' (24h). Returns None if invalid."""
    m = TIME_RE.match(token.strip())
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    meridiem = (m.group(3) or "").lower()
    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"


class TelegramService:
    """Service layer for handling Telegram-specific business logic"""

    def __init__(self, db=None):
        self.logger = get_logger()
        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        self._db = db
        self._sub_repo = None
        self._user_repo = None
        self._msg_repo = None
        self._cmd_log_repo = None

    # ------------------------------------------------------------------
    # Lazy repo accessors
    # ------------------------------------------------------------------

    def _get_db(self):
        if self._db:
            return self._db
        from core.context import get_db
        return get_db()

    def _get_sub_repo(self):
        if self._sub_repo is None:
            db = self._get_db()
            if db:
                from repo.subscription_repo import SubscriptionRepository
                self._sub_repo = SubscriptionRepository(db)
        return self._sub_repo

    def _get_user_repo(self):
        if self._user_repo is None:
            db = self._get_db()
            if db:
                from repo.user_repo import UserRepository
                self._user_repo = UserRepository(db)
        return self._user_repo

    def _get_msg_repo(self):
        if self._msg_repo is None:
            db = self._get_db()
            if db:
                from repo.message_repo import MessageRepository
                self._msg_repo = MessageRepository(db)
        return self._msg_repo

    def _get_cmd_log_repo(self):
        if self._cmd_log_repo is None:
            db = self._get_db()
            if db:
                from repo.command_log_repo import CommandLogRepository
                self._cmd_log_repo = CommandLogRepository(db)
        return self._cmd_log_repo

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _track_user(self, message: Dict[str, Any]) -> None:
        repo = self._get_user_repo()
        if not repo:
            return
        chat_id = message["chat"]["id"]
        sender = message.get("from", {})
        username = sender.get("username")
        first = sender.get("first_name", "")
        last = sender.get("last_name", "")
        full_name = f"{first} {last}".strip() or None
        repo.upsert(chat_id, username, full_name)

    def _log_in(self, chat_id: int, text: str, message_type: str = "text") -> None:
        r = self._get_msg_repo()
        if r:
            r.insert(chat_id, "in", text, message_type)

    def _log_out(self, chat_id: int, text: str, message_type: str = "text") -> None:
        r = self._get_msg_repo()
        if r:
            r.insert(chat_id, "out", text, message_type)

    def _log_cmd(self, chat_id: int, command: str, args: str = "",
                 status: str = "ok", error_msg: str = None) -> None:
        r = self._get_cmd_log_repo()
        if r:
            r.insert(chat_id, command, args or None, status, error_msg)

    # ------------------------------------------------------------------
    # Main message handler
    # ------------------------------------------------------------------

    async def process_message(self, message: Dict[str, Any]) -> bool:
        try:
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            self.logger.info(f"[{TAG}] Message from {chat_id}: {text}")

            if not text:
                return False

            self._track_user(message)
            msg_type = "command" if text.startswith("/") else "text"
            self._log_in(chat_id, text, msg_type)

            if text.startswith("/"):
                await self._handle_command(chat_id, text)
            else:
                response = f"Echo: {text}"
                await self.bot.send_message(chat_id, response)
                self._log_out(chat_id, response)

            return True
        except Exception as e:
            self.logger.error(f"[{TAG}] Error processing message: {e}")
            return False

    # ------------------------------------------------------------------
    # Command routing
    # ------------------------------------------------------------------

    async def _handle_command(self, chat_id: int, text: str) -> None:
        parts = text.lstrip("/").split()
        cmd = parts[0].lower().split("@")[0]
        args = parts[1:]
        args_str = " ".join(args)
        status = "ok"
        error_msg = None

        try:
            if cmd in ("help", "start"):
                await self.bot.send_message(
                    chat_id, MAIN_MENU_TEXT,
                    mode_html=True,
                    reply_markup=MAIN_MENU_KEYBOARD
                )

            elif cmd == "status":
                await self._cmd_status(chat_id)

            elif cmd in SUB_COMMANDS:
                await self._cmd_set(chat_id, SUB_COMMANDS[cmd], args)

            elif cmd in UNSET_COMMANDS:
                await self._cmd_unset(chat_id, UNSET_COMMANDS[cmd])

            else:
                await self.bot.send_message(
                    chat_id,
                    "❓ Lệnh không hợp lệ. Nhấn /help để xem menu."
                )

        except Exception as e:
            status = "error"
            error_msg = str(e)
            raise
        finally:
            self._log_cmd(chat_id, f"/{cmd}", args_str, status, error_msg)

    # ------------------------------------------------------------------
    # Callback query handler (button clicks)
    # ------------------------------------------------------------------

    async def handle_callback_query(self, callback_query: Dict[str, Any]) -> bool:
        try:
            query_id = callback_query["id"]
            data = callback_query.get("data", "")
            chat_id = callback_query["message"]["chat"]["id"]
            message_id = callback_query["message"]["message_id"]

            self.logger.info(f"[{TAG}] Callback from {chat_id}: {data}")
            self._log_in(chat_id, f"[button] {data}", "command")

            await self._route_callback(chat_id, message_id, data)
            await self.bot.answer_callback_query(query_id)
            return True

        except Exception as e:
            self.logger.error(f"[{TAG}] Error handling callback: {e}")
            return False

    async def _route_callback(self, chat_id: int, message_id: int, data: str) -> None:
        # --- Main menu ---
        if data == "menu":
            await self.bot.edit_message_text(
                chat_id, message_id,
                MAIN_MENU_TEXT,
                mode_html=True,
                reply_markup=MAIN_MENU_KEYBOARD
            )
            return

        # --- Instant fetch ---
        if data == "get_weather":
            from services.weather import WeatherService
            content = await WeatherService().get_weather()
            await self.bot.send_message(chat_id, content, mode_html=True)
            self._log_out(chat_id, content)
            return

        if data == "get_news":
            from services.news import NewsService
            content = await NewsService().get_news()
            await self.bot.send_message(chat_id, content, mode_html=True)
            self._log_out(chat_id, content)
            return

        if data == "get_gold":
            from services.gold_price import GoldPriceService
            content = await GoldPriceService().get_gold_price()
            await self.bot.send_message(chat_id, content, mode_html=True)
            self._log_out(chat_id, content)
            return

        # --- Time picker ---
        if data.startswith("time_pick:"):
            sub_type = data.split(":", 1)[1]
            await self.bot.edit_message_text(
                chat_id, message_id,
                time_picker_text(sub_type),
                mode_html=True,
                reply_markup=time_picker_keyboard(sub_type)
            )
            return

        # --- Set subscription: set:<type>:<HH:MM> ---
        if data.startswith("set:"):
            _, sub_type, scheduled_time = data.split(":", 2)
            await self._cb_set(chat_id, message_id, sub_type, scheduled_time)
            return

        # --- Unset subscription: unset:<type> ---
        if data.startswith("unset:"):
            sub_type = data.split(":", 1)[1]
            await self._cb_unset(chat_id, message_id, sub_type)
            return

        # --- Status / subscription management ---
        if data == "status":
            await self._cb_status(chat_id, message_id)
            return

    # ------------------------------------------------------------------
    # Subscription logic (shared by commands and callbacks)
    # ------------------------------------------------------------------

    async def _cb_set(self, chat_id: int, message_id: int,
                      sub_type: str, scheduled_time: str) -> None:
        labels = {"weather": "thời tiết", "news": "tin tức", "gold_price": "giá vàng"}
        label = labels.get(sub_type, sub_type)
        repo = self._get_sub_repo()

        if repo and repo.upsert(chat_id, sub_type, scheduled_time, "daily"):
            text = f"✅ Đã đặt thông báo <b>{label}</b> lúc <b>{scheduled_time}</b> hàng ngày."
            self._log_cmd(chat_id, f"set:{sub_type}", scheduled_time)
        else:
            text = "⚠️ Không thể lưu đăng ký, thử lại sau."

        await self.bot.edit_message_text(
            chat_id, message_id, text,
            mode_html=True,
            reply_markup={"inline_keyboard": [[
                {"text": "← Quay lại", "callback_data": "menu"}
            ]]}
        )
        self._log_out(chat_id, text, "command")

    async def _cb_unset(self, chat_id: int, message_id: int, sub_type: str) -> None:
        labels = {"weather": "thời tiết", "news": "tin tức", "gold_price": "giá vàng"}
        label = labels.get(sub_type, sub_type)
        repo = self._get_sub_repo()

        if repo and repo.deactivate(chat_id, sub_type):
            text = f"✅ Đã hủy thông báo <b>{label}</b>."
            self._log_cmd(chat_id, f"unset:{sub_type}", "", "ok")
        else:
            text = f"ℹ️ Bạn không có đăng ký <b>{label}</b> nào đang hoạt động."

        await self.bot.edit_message_text(
            chat_id, message_id, text,
            mode_html=True,
            reply_markup={"inline_keyboard": [[
                {"text": "← Quay lại menu", "callback_data": "menu"}
            ]]}
        )
        self._log_out(chat_id, text, "command")

    async def _cb_status(self, chat_id: int, message_id: int) -> None:
        repo = self._get_sub_repo()
        subs = repo.get_by_chat_id(chat_id) if repo else []

        if not subs:
            text = "ℹ️ Bạn chưa có đăng ký nào đang hoạt động."
            keyboard = {"inline_keyboard": [[
                {"text": "← Quay lại", "callback_data": "menu"}
            ]]}
        else:
            label_map = {"weather": "🌤 Thời tiết", "news": "📰 Tin tức", "gold_price": "🥇 Giá vàng"}
            lines = ["<b>Đăng ký hiện tại của bạn:</b>"]
            for sub in subs:
                lines.append(f"• {label_map.get(sub.subscription_type, sub.subscription_type)} — <b>{sub.scheduled_time}</b>")
            text = "\n".join(lines)
            active_types = [s.subscription_type for s in subs]
            keyboard = status_keyboard(active_types)

        await self.bot.edit_message_text(
            chat_id, message_id, text,
            mode_html=True, reply_markup=keyboard
        )
        self._log_out(chat_id, text, "command")

    # ------------------------------------------------------------------
    # Text command handlers (fallback if users type commands manually)
    # ------------------------------------------------------------------

    async def _cmd_status(self, chat_id: int) -> None:
        repo = self._get_sub_repo()
        subs = repo.get_by_chat_id(chat_id) if repo else []
        if not subs:
            await self.bot.send_message(chat_id, "ℹ️ Bạn chưa có đăng ký nào.")
            return
        label_map = {"weather": "🌤 Thời tiết", "news": "📰 Tin tức", "gold_price": "🥇 Giá vàng"}
        lines = ["<b>Đăng ký hiện tại:</b>"]
        for sub in subs:
            lines.append(f"• {label_map.get(sub.subscription_type, sub.subscription_type)} — <b>{sub.scheduled_time}</b>")
        active_types = [s.subscription_type for s in subs]
        await self.bot.send_message(
            chat_id, "\n".join(lines),
            mode_html=True, reply_markup=status_keyboard(active_types)
        )

    async def _cmd_set(self, chat_id: int, sub_type: str, args: list) -> None:
        if not args:
            await self.bot.send_message(
                chat_id,
                f"❌ Thiếu giờ. Ví dụ: /set-weather 7am daily\n\nHoặc dùng menu:",
                reply_markup={"inline_keyboard": [[
                    {"text": "⏰ Chọn giờ", "callback_data": f"time_pick:{sub_type}"}
                ]]}
            )
            return
        time_str = parse_time(args[0])
        if not time_str:
            await self.bot.send_message(
                chat_id, "❌ Định dạng giờ không hợp lệ. Dùng: 7am · 7:30am · 07:00 · 14:30"
            )
            return
        repo = self._get_sub_repo()
        labels = {"weather": "thời tiết", "news": "tin tức", "gold_price": "giá vàng"}
        if repo and repo.upsert(chat_id, sub_type, time_str, "daily"):
            await self.bot.send_message(
                chat_id,
                f"✅ Đã đặt thông báo <b>{labels.get(sub_type)}</b> lúc <b>{time_str}</b> hàng ngày.",
                mode_html=True,
                reply_markup={"inline_keyboard": [[
                    {"text": "📋 Xem đăng ký", "callback_data": "status"},
                    {"text": "← Menu", "callback_data": "menu"},
                ]]}
            )
        else:
            await self.bot.send_message(chat_id, "⚠️ Không thể lưu đăng ký, thử lại sau.")

    async def _cmd_unset(self, chat_id: int, sub_type: str) -> None:
        labels = {"weather": "thời tiết", "news": "tin tức", "gold_price": "giá vàng"}
        repo = self._get_sub_repo()
        if repo and repo.deactivate(chat_id, sub_type):
            await self.bot.send_message(
                chat_id,
                f"✅ Đã hủy thông báo <b>{labels.get(sub_type, sub_type)}</b>.",
                mode_html=True
            )
        else:
            await self.bot.send_message(
                chat_id,
                f"ℹ️ Bạn không có đăng ký <b>{labels.get(sub_type, sub_type)}</b> nào.",
                mode_html=True
            )

    async def send_message(self, chat_id: int, text: str, mode_html: bool = False) -> Dict[str, Any]:
        return await self.bot.send_message(chat_id, text, mode_html)

    async def handle_edited_message(self, edited_message: Dict[str, Any]) -> bool:
        try:
            chat_id = edited_message["chat"]["id"]
            text = edited_message.get("text", "")
            self.logger.info(f"[{TAG}] Edited message from {chat_id}: {text}")
            return True
        except Exception as e:
            self.logger.error(f"[{TAG}] Error handling edited message: {e}")
            return False
