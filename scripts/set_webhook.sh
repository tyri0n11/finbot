set -e

# Lấy public URL từ ngrok API
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels \
  | jq -r '.tunnels[0].public_url')

if [ -z "$NGROK_URL" ] || [ "$NGROK_URL" == "null" ]; then
  echo "❌ Không lấy được ngrok URL. Ngrok có chạy chưa?"
  exit 1
fi

WEBHOOK_URL="${NGROK_URL}/webhook"

echo "✅ Ngrok URL: $NGROK_URL"
echo "➡️  Đặt webhook: $WEBHOOK_URL"

# Gọi API Telegram
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${WEBHOOK_URL}\"}" \
  | jq .
