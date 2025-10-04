# FinBot Backend 🤖💰

A sophisticated **Financial Management Bot Backend** built with modern Python technologies, designed to help users track their personal finances through a Telegram bot interface.

## 🚀 Project Overview

FinBot is a comprehensive financial management system that provides users with an intelligent way to track expenses, income, and loans through a conversational Telegram bot interface. The backend is architected using modern software engineering principles, featuring clean architecture, type safety, and containerized deployment.

## 🛠️ Tech Stack & Technical Skills Demonstrated

### **Core Backend Technologies**
- **FastAPI** - Modern, high-performance web framework for building APIs
- **Pydantic V2** - Advanced data validation and serialization with type safety
- **Uvicorn** - Lightning-fast ASGI server

### **Database & Data Management**
- **ClickHouse** - High-performance columnar database for analytics workloads
- **Pydantic Settings** - Configuration management with environment variable support

### **Bot Development**
- **Aiogram** - Asynchronous Telegram Bot API framework
- **Webhook Architecture** - Real-time message processing
- **ngrok Integration** - Development environment tunneling

### **DevOps & Infrastructure**
- **Docker & Docker Compose** - Containerization and orchestration
- **Multi-stage Dockerfile** - Optimized container builds
- **Makefile** - Automated development workflows
- **Environment Configuration** - Structured settings management

### **Software Engineering Practices**
- **Clean Architecture** - Separation of concerns with layered structure
- **Dependency Injection** - Modular and testable code design
- **Type Safety** - Comprehensive type hints throughout the codebase
- **Validation Layer** - Business logic validation with Pydantic validators
- **Factory Pattern** - Application factory for flexible configuration

## 📁 Project Architecture

```
finbot-be/
├── app/                    # Application core
│   ├── api/               # API layer
│   │   └── v1/           # API versioning
│   ├── core/             # Core configurations
│   │   ├── database.py   # Database connections
│   │   ├── settings.py   # Environment settings
│   │   └── setup.py      # Application factory
│   ├── model/            # Data models
│   │   └── transaction.py # Transaction entities
│   ├── repo/             # Repository pattern
│   └── services/         # Business logic layer
├── Docker/               # Container configurations
├── scripts/              # Automation scripts
└── compose.yaml          # Docker orchestration
```

## 🔧 Key Features & Technical Implementations

### **1. Advanced Data Modeling**
```python
# Sophisticated transaction model with enum validation
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: TransactionType
    amount: float
    category: Optional[str] = None
    
    @validator("category", always=True)
    def validate_category(cls, v, values):
        # Dynamic validation based on transaction type
```

### **2. Type-Safe Configuration Management**
```python
class Settings(ProjectSettings, ClickHouseSettings, TelegramBotSettings):
    # Multiple inheritance for modular configuration
    pass
```

### **3. Application Factory Pattern**
```python
def create_application(router: APIRouter, settings: SettingType) -> FastAPI:
    # Flexible app creation with dependency injection
```

### **4. Financial Transaction Categories**
- **Expense Categories**: Food, Transport, Entertainment, Utilities, Health, Education
- **Income Categories**: Salary, Investment, Bonus
- **Loan Categories**: Pay Debt, Borrow, Lend

## 🐳 Containerized Development Environment

### **Docker Compose Setup**
- **ClickHouse Database** with persistent storage
- **Backend Service** with hot-reload development
- **Network Isolation** for security
- **Environment Variable Management**

### **Development Workflow**
```bash
make up       # Start all services
make down     # Stop all services
make restart  # Restart with rebuild
make logs     # View service logs
```

## 🔐 Configuration Management

**Environment-based Settings**:
- ClickHouse connection parameters
- Telegram Bot API tokens
- Project metadata
- Development/Production modes

## 📊 Database Design

**ClickHouse Integration**:
- High-performance analytics database
- Optimized for financial transaction queries
- Scalable data storage for user analytics

## 🤖 Telegram Bot Integration

**Webhook Architecture**:
- Real-time message processing
- Automated webhook configuration
- ngrok development tunneling
- Secure API token management

## 🚀 Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finbot-be
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Configure your environment variables
   ```

3. **Start Development Environment**
   ```bash
   make up
   ```

4. **Access Services**
   - API: `http://localhost:8000`
   - ClickHouse: `http://localhost:8123`

## 🧪 Code Quality & Standards

- **Type Safety**: Comprehensive type hints throughout
- **Validation**: Business logic validation with Pydantic
- **Error Handling**: Structured exception management
- **Code Formatting**: Black formatter integration
- **Modular Design**: Clean separation of concerns

## 📈 Technical Highlights for CV

This project demonstrates proficiency in:

✅ **Modern Python Development** - FastAPI, Pydantic V2, Python 3.12
✅ **Database Technologies** - ClickHouse, SQL, Data Modeling
✅ **API Development** - RESTful APIs, OpenAPI/Swagger, Async Programming
✅ **Bot Development** - Telegram Bot API, Webhook Architecture
✅ **DevOps & Containerization** - Docker, Docker Compose, Container Orchestration
✅ **Software Architecture** - Clean Architecture, Dependency Injection, Factory Pattern
✅ **Configuration Management** - Environment Variables, Settings Management
✅ **Development Workflows** - Makefile Automation, Development Environment Setup
✅ **Financial Domain Knowledge** - Transaction Management, Financial Categorization

## 🎯 Future Enhancements

- [ ] Comprehensive test suite with pytest
- [ ] CI/CD pipeline with GitHub Actions
- [ ] API documentation with Swagger UI
- [ ] Database migrations system
- [ ] Monitoring and logging integration
- [ ] API rate limiting and security features

---

**Built with ❤️ and modern Python technologies**