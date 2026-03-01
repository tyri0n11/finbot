# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start full stack (builds images, starts containers, sets Telegram webhook)
make up

# Stop all services
make down

# Tail all container logs
make logs

# Format code with black (excludes storage/ and migrations/)
make format

# Destroy containers and volumes (data loss)
make reset

# Show running container status
make ps
```

The backend runs at `http://localhost:8000`, ClickHouse HTTP UI at `http://localhost:8123`, ngrok inspector at `http://localhost:4040`, and Jenkins at `http://localhost:8080`.

There are no test commands configured yet.

## Environment Setup

```bash
cp .env.example .env
# Fill in TELEGRAM_BOT_TOKEN and NGROK_AUTHTOKEN before running make up
```

## Architecture

FinBot is a Telegram-based personal finance tracker. Users send natural language messages (e.g. Vietnamese text like `"đổ xăng - 20k"`), which the bot parses into structured transactions and stores in dual databases.

### Request Flow

1. **Webhook auto-registration**: On startup, `WebhookManager` (`app/core/webhook.py`) polls the ngrok API every 10 seconds, detects the public HTTPS URL, and calls Telegram's `setWebhook` to register it automatically.
2. **Incoming updates**: Telegram POSTs to `/webhook` → `WebhookService` (`app/services/webhook.py`) routes by update type → `TelegramService` (`app/services/telegram.py`) handles message processing.
3. **Data storage**: Transactions go to **PostgreSQL** (OLTP, transactional) and are streamed to **ClickHouse** (OLAP, analytics/reporting).

### Module Structure

The **Python module root is `app/`** (set via `PYTHONPATH=/app`). All imports are relative to `app/`:

```
app/
├── main.py              # FastAPI app entry point
├── core/
│   ├── setup.py         # App factory (create_application)
│   ├── settings.py      # Pydantic settings (env vars via pydantic_settings)
│   ├── database.py      # Database class: ClickHouse + PostgreSQL connection pool
│   ├── webhook.py       # WebhookManager: ngrok polling + Telegram webhook registration
│   ├── telegram_bot.py  # TelegramBot: raw Telegram Bot API HTTP client
│   └── logger.py        # Logger factory
├── api/
│   ├── __init__.py      # Root router at /api
│   └── v1/
│       ├── __init__.py  # v1 router at /api/v1
│       ├── health.py    # Health check endpoint
│       └── webhook.py   # Webhook router at /webhook (mounted at root, not /api)
├── services/
│   ├── webhook.py       # WebhookService: routes Telegram update types
│   └── telegram.py      # TelegramService: message processing and bot replies
├── model/
│   └── transaction.py   # Transaction Pydantic model with category enums (Vietnamese values)
└── repo/                # Repository layer (currently empty, for DB access patterns)
```

### Key Architectural Notes

- **Dual router mounting**: The webhook endpoint (`/webhook`) is mounted directly on the app root in `main.py`, bypassing the `/api` prefix. Health and other routes go under `/api/v1/`.
- **App factory pattern**: `create_application()` in `core/setup.py` wires together middleware, routers, and startup/shutdown lifecycle hooks.
- **Settings**: All config via environment variables using `pydantic_settings.BaseSettings`. Multiple settings classes are composed via multiple inheritance into a single `Settings` class.
- **Database**: `Database` class manages both a ClickHouse client and a psycopg2 `SimpleConnectionPool`. It is instantiated once on startup.
- **Transaction categories**: Enum values are in Vietnamese (`"chi"`, `"thu"`, `"vay"` for types; e.g. `"Ăn uống"` for Food).
- **`app/` volume mount**: In `compose.yaml`, `./app` is mounted to `/app` inside the container with `--reload`, so code changes take effect without rebuilding.
