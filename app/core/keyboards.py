"""
Telegram inline keyboard layouts for FinBot.

Callback data format:
  menu                    → show main menu
  get_weather             → fetch weather now
  get_news                → fetch news now
  get_gold                → fetch gold price now
  time_pick:weather       → show time picker for weather
  time_pick:news          → show time picker for news
  time_pick:gold_price    → show time picker for gold price
  set:weather:07:00       → subscribe weather at 07:00
  set:news:08:00          → subscribe news at 08:00
  set:gold_price:09:00    → subscribe gold price at 09:00
  unset:weather           → cancel weather subscription
  unset:news              → cancel news subscription
  unset:gold_price        → cancel gold price subscription
  status                  → show active subscriptions
"""

# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MAIN_MENU_TEXT = (
    "🤖 <b>FinBot – Trợ lý tài chính cá nhân</b>\n\n"
    "Chọn chức năng bạn muốn:"
)

MAIN_MENU_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "🌤 Thời tiết",  "callback_data": "get_weather"},
            {"text": "📰 Tin tức",    "callback_data": "get_news"},
            {"text": "🥇 Giá vàng",  "callback_data": "get_gold"},
        ],
        [
            {"text": "⏰ Hẹn thời tiết",  "callback_data": "time_pick:weather"},
            {"text": "⏰ Hẹn tin tức",    "callback_data": "time_pick:news"},
        ],
        [
            {"text": "⏰ Hẹn giá vàng",   "callback_data": "time_pick:gold_price"},
            {"text": "📋 Đăng ký của tôi", "callback_data": "status"},
        ],
    ]
}

# ---------------------------------------------------------------------------
# Time picker
# ---------------------------------------------------------------------------

_TIMES = ["06:00", "07:00", "08:00", "09:00", "10:00",
          "12:00", "15:00", "18:00", "20:00", "22:00"]

_LABELS = {
    "weather":    "thời tiết",
    "news":       "tin tức",
    "gold_price": "giá vàng",
}


def time_picker_keyboard(sub_type: str) -> dict:
    label = _LABELS.get(sub_type, sub_type)
    rows = []

    # 3 buttons per row
    row = []
    for t in _TIMES:
        row.append({"text": t, "callback_data": f"set:{sub_type}:{t}"})
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([{"text": "← Quay lại", "callback_data": "menu"}])
    return {"inline_keyboard": rows}


def time_picker_text(sub_type: str) -> str:
    label = _LABELS.get(sub_type, sub_type)
    return f"⏰ Chọn giờ nhận thông báo <b>{label}</b> hàng ngày:"


# ---------------------------------------------------------------------------
# Status / unsubscribe
# ---------------------------------------------------------------------------

def status_keyboard(active_types: list) -> dict:
    """Build unsubscribe buttons for each active subscription."""
    label_map = {
        "weather":    "🌤 Thời tiết",
        "news":       "📰 Tin tức",
        "gold_price": "🥇 Giá vàng",
    }
    rows = []
    for sub_type in active_types:
        label = label_map.get(sub_type, sub_type)
        rows.append([{
            "text": f"❌ Hủy {label}",
            "callback_data": f"unset:{sub_type}"
        }])
    rows.append([{"text": "← Quay lại", "callback_data": "menu"}])
    return {"inline_keyboard": rows}
