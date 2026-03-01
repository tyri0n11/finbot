import httpx
from core.logger import get_logger

TAG = "GoldPriceService"

SJC_URL = "https://sjc.com.vn/GoldPrice/GetGoldPriceList"


class GoldPriceService:
    def __init__(self):
        self.logger = get_logger()

    async def get_gold_price(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(SJC_URL)

            if not r.is_success:
                self.logger.error(f"[{TAG}] SJC API error {r.status_code}: {r.text}")
                return "⚠️ Không thể lấy giá vàng SJC."

            data = r.json()
            items = data if isinstance(data, list) else data.get("data", [])

            # Look for SJC 1-tael entry
            buy_price = sell_price = None
            for item in items:
                name = str(item.get("kieu", "") or item.get("name", "") or item.get("Name", "")).lower()
                if "1" in name and ("tael" in name or "lượng" in name or "sjc" in name.lower()):
                    buy_price = item.get("mua") or item.get("buy") or item.get("Buy")
                    sell_price = item.get("ban") or item.get("sell") or item.get("Sell")
                    break

            # Fallback: use first item
            if buy_price is None and items:
                first = items[0]
                buy_price = first.get("mua") or first.get("buy") or first.get("Buy")
                sell_price = first.get("ban") or first.get("sell") or first.get("Sell")

            if buy_price is None:
                return "⚠️ Không thể phân tích dữ liệu giá vàng."

            def fmt(val) -> str:
                try:
                    return f"{int(val):,}".replace(",", ".")
                except (ValueError, TypeError):
                    return str(val)

            return (
                f"🥇 <b>Giá vàng SJC hôm nay</b>\n"
                f"💰 Mua vào: <b>{fmt(buy_price)} VNĐ</b>\n"
                f"💵 Bán ra: <b>{fmt(sell_price)} VNĐ</b>"
            )
        except Exception as e:
            self.logger.error(f"[{TAG}] Failed to fetch gold price: {e}")
            return "⚠️ Lỗi khi lấy giá vàng."
