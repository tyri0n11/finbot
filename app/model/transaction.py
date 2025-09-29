from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import uuid


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
    OTHER = "Khác"


class IncomeCategory(str, Enum):
    SALARY = "Lương"
    INVESTMENT = "Đầu tư"
    BONUS = "Thưởng"


class LoanCategory(str, Enum):
    PAY_DEBT = "Trả nợ"
    BORROW = "Đi vay"
    LEND = "Cho vay"


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: TransactionType
    amount: float
    currency: str = "VND"
    category: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

    @validator("category", always=True)
    def validate_category(cls, v, values):
        t_type = values.get("type")
        if t_type == TransactionType.EXPENSE:
            if v not in [c.value for c in ExpenseCategory]:
                raise ValueError(f"Category must be one of {list(ExpenseCategory)}")
        elif t_type == TransactionType.INCOME:
            if v not in [c.value for c in IncomeCategory]:
                raise ValueError(f"Category must be one of {list(IncomeCategory)}")
        elif t_type == TransactionType.LOAN:
            if v not in [c.value for c in LoanCategory]:
                raise ValueError(f"Category must be one of {list(LoanCategory)}")
        return v

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v
