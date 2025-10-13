
## 🚀 Project Overview

FinBot is built as a **clean, modular backend system** showcasing real-world engineering practices:

* Users interact via a Telegram bot.
* The bot extracts intent (e.g. *“đổ xăng - 20k” → Expense → Transport → Fuel*).
* Transactions are stored in **PostgreSQL** (OLTP).
* Data is streamed into **ClickHouse** for **analytics & reporting**.
* The backend is fully **containerized, configurable, and scalable**.

---

## 🛠️ Tech Stack & Skills Demonstrated

### **Backend**

* **FastAPI** – high-performance async API framework
* **Pydantic V2** – type-safe data validation
* **Uvicorn** – ASGI server

### **Databases**

* **PostgreSQL** – reliable OLTP storage
* **ClickHouse** – high-performance OLAP analytics
* **CDC/Event-driven sync** – data pipeline between OLTP ↔ OLAP

### **AI & NLP**

* **Ollama (self-hosted LLMs)** – natural language parsing
* **Hybrid intent detection** – regex + LLM fallback
* **Structured financial categorization**

### **Bot Development**

* **Aiogram** – async Telegram Bot framework
* **Webhook-based** – real-time message processing
* **ngrok** – local development tunneling

### **DevOps & Infra**

* **Docker & Docker Compose** – container orchestration
* **Multi-stage builds** – optimized images
* **Makefile** – streamlined workflows
* **Environment-based configuration**

### **Engineering Practices**

* **Clean Architecture** – separation of concerns
* **Dependency Injection** – modular, testable design
* **Factory Pattern** – flexible app setup
* **Validation Layer** – domain logic with Pydantic

---

## 📁 Project Structure

```
finbot-be/
├── app/
│   ├── api/            # API layer
│   ├── core/           # Settings & app factory
│   ├── model/          # Data models
│   ├── repo/           # Repository pattern
│   └── services/       # Business logic
├── Docker/             # Container configs
├── scripts/            # Automation scripts
└── compose.yaml        # Orchestration
```

---

## 🔧 Key Features

1. **Intelligent NLP Parsing**

   * Input: `"đổ xăng - 20k"`
   * Output: `Expense → Transport → Fuel → 20,000 VND`
   * Hybrid: Regex rules + Ollama-powered LLM

2. **Hybrid Data Architecture**

   * **PostgreSQL (OLTP)** – transactional storage
   * **ClickHouse (OLAP)** – fast analytics & reports

3. **Containerized Development**

   * `make up` → start full stack (bot, API, DBs, analytics)
   * Hot-reload & logs available

---

## 📊 Financial Categories

* **Expenses** – Food, Transport, Entertainment, Utilities, Health, Education
* **Income** – Salary, Investments, Bonus
* **Loans** – Borrow, Lend, Repayment

---

## 🐳 Quick Start

```bash
git clone <repository-url>
cd finbot-be

cp .env.example .env   # Configure env variables
make up                # Start services
```

* API → `http://localhost:8000`
* ClickHouse UI → `http://localhost:8123`

---

## 📈 Skills Highlighted

✅ **Backend Engineering** – FastAPI, PostgreSQL, async APIs
✅ **Data Engineering** – OLTP → OLAP pipelines with ClickHouse
✅ **AI/NLP Integration** – Self-hosted LLM (Ollama) for intent detection
✅ **Bot Development** – Telegram Bot (Aiogram, Webhooks)
✅ **DevOps** – Docker, Compose, Makefile automation
✅ **Software Architecture** – Clean Architecture, DI, Factory Pattern
