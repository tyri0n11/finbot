"""
Domain models for the application
"""

from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class MessageType(Enum):
    """Enumeration of message types that can be parsed"""
    COMMAND = "command"
    TRANSACTION = "transaction"
    JSON = "json"
    KEY_VALUE = "key_value"
    TEXT = "text"
    UNKNOWN = "unknown"


class ParseResult:
    """
    Standard result object returned by all parsers
    """
    def __init__(self, 
                 message_type: MessageType, 
                 data: Dict[str, Any], 
                 original_message: str,
                 confidence: float = 1.0,
                 errors: list = None,
                 parser_name: str = ""):
        self.message_type = message_type
        self.data = data
        self.original_message = original_message
        self.confidence = confidence
        self.errors = errors or []
        self.parser_name = parser_name
        self.timestamp = self._get_timestamp()
    
    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()
    
    def is_successful(self) -> bool:
        """Check if parsing was successful"""
        return self.message_type != MessageType.UNKNOWN and not self.errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.message_type.value,
            "data": self.data,
            "original_message": self.original_message,
            "confidence": self.confidence,
            "errors": self.errors,
            "timestamp": self.timestamp,
            "parser_name": self.parser_name
        }


class TransactionType(str, Enum):
    EXPENSE = "chi"
    INCOME = "thu"
    LOAN = "vay"


class ExpenseCategory(str, Enum):
    FOOD = "Ăn uống"
    TRANSPORT = "Di chuyển"
    ENTERTAINMENT = "Giải trí"
    UTILITIES = "Tiện ích"
    HEALTH = "Sức khỏe"
    EDUCATION = "Giáo dục"
    SHOPPING = "Mua sắm"
    OTHER = "Khác"


class IncomeCategory(str, Enum):
    SALARY = "Lương"
    INVESTMENT = "Đầu tư"
    BONUS = "Thưởng"


class LoanCategory(str, Enum):
    PAY_DEBT = "Trả nợ"
    BORROW = "Đi vay"
    LEND = "Cho vay"


class Currency(str, Enum):
    VND = "VND"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    chat_id: Optional[int] = None
    type: TransactionType
    amount: float
    currency: Currency = Currency.VND
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    raw_text: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        use_enum_values = True

    @validator("category", always=True)
    def validate_category(cls, v, values):
        if not v:
            return None
        
        transaction_type = values.get("type")
        if transaction_type == TransactionType.EXPENSE:
            if v not in [cat.value for cat in ExpenseCategory]:
                return ExpenseCategory.OTHER.value
        elif transaction_type == TransactionType.INCOME:
            if v not in [cat.value for cat in IncomeCategory]:
                return v  # Allow custom income categories
        elif transaction_type == TransactionType.LOAN:
            if v not in [cat.value for cat in LoanCategory]:
                return v  # Allow custom loan categories
        
        return v

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class CommandData(BaseModel):
    """Model for command data"""
    command: str
    original_command: str
    args: list = Field(default_factory=list)
    action: str
    description: str = ""
    response_type: str = "text"


class TelegramMessage(BaseModel):
    """Model for Telegram message"""
    message_id: int
    chat_id: int
    user_id: int
    text: str
    date: int
    first_name: Optional[str] = None
    username: Optional[str] = None
