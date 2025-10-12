"""
Validation utilities
"""

import json
import re
from typing import Any, Dict


def is_valid_json(text: str) -> bool:
    """
    Check if text is valid JSON
    
    Args:
        text: Text to validate
        
    Returns:
        bool: True if valid JSON
    """
    try:
        json.loads(text.strip())
        return True
    except json.JSONDecodeError:
        return False


def is_command(text: str) -> bool:
    """
    Check if text is a bot command
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if it's a command
    """
    return text.strip().startswith('/')


def is_transaction_message(text: str) -> bool:
    """
    Check if text contains transaction indicators (expenses and income)
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if it looks like a transaction
    """
    text_lower = text.lower()
    
    # Vietnamese expense verbs
    vietnamese_expense_verbs = [
        'mua', 'chi', 'trả', 'mất', 'tốn', 'đi', 'ăn', 'uống', 
        'thuê', 'đóng', 'nạp', 'rút', 'chuyển', 'gửi'
    ]
    
    # Vietnamese income verbs/keywords
    vietnamese_income_verbs = [
        'nhận', 'được', 'thu', 'kiếm', 'bán', 'lương', 'thưởng',
        'thu nhập', 'tiền lương', 'tiền thưởng', 'tiền bán',
        'được trả', 'được nhận', 'freelance', 'làm thêm', 'kiếm được'
    ]
    
    # English transaction words
    english_expense_words = [
        'spent', 'paid', 'bought', 'purchased', 'cost', 'price'
    ]
    
    english_income_words = [
        'earned', 'received', 'got', 'salary', 'bonus', 'income',
        'freelance', 'commission', 'sold', 'revenue'
    ]
    
    # Currency indicators
    has_currency = bool(re.search(r'[\$€£]|\d+(?:\.\d+)?\s*(?:usd|eur|gbp|vnd|đ|tr|m|k)', text_lower))
    has_vietnamese_expense_verb = any(verb in text_lower for verb in vietnamese_expense_verbs)
    has_vietnamese_income_verb = any(verb in text_lower for verb in vietnamese_income_verbs)
    has_english_expense_word = any(word in text_lower for word in english_expense_words)
    has_english_income_word = any(word in text_lower for word in english_income_words)
    
    return (has_currency or 
            has_vietnamese_expense_verb or 
            has_vietnamese_income_verb or 
            has_english_expense_word or 
            has_english_income_word)


def validate_amount(amount: Any) -> bool:
    """
    Validate if amount is a valid positive number
    
    Args:
        amount: Amount to validate
        
    Returns:
        bool: True if valid
    """
    try:
        num = float(amount)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_currency(currency: str) -> bool:
    """
    Validate if currency is supported
    
    Args:
        currency: Currency code to validate
        
    Returns:
        bool: True if supported
    """
    supported_currencies = ['VND', 'USD', 'EUR', 'GBP']
    return currency.upper() in supported_currencies


def clean_and_validate_text(text: str, max_length: int = 1000) -> str:
    """
    Clean and validate text input
    
    Args:
        text: Text to clean
        max_length: Maximum allowed length
        
    Returns:
        str: Cleaned text
        
    Raises:
        ValueError: If text is invalid
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string")
    
    cleaned = text.strip()
    
    if not cleaned:
        raise ValueError("Text cannot be empty")
    
    if len(cleaned) > max_length:
        raise ValueError(f"Text too long (max {max_length} characters)")
    
    return cleaned